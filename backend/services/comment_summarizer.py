"""
会社コメント要約サービス

Gemini API（無料枠）を優先し、フォールバックとしてClaude API、
最終手段としてローカルキーワードベース要約を使用する。
"""

from typing import Dict, List, Optional, Tuple
import os
import re


def summarize_with_gemini(comment_text: str, section_name: str) -> str:
    """
    Gemini APIでコメントを要約

    Args:
        comment_text: 要約対象のテキスト
        section_name: セクション名

    Returns:
        HTML箇条書き形式の要約テキスト（失敗時は空文字列）
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return ""

    if not comment_text or len(comment_text.strip()) < 50:
        return ""

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)

        prompt = f"""以下は決算短信の「{section_name}」セクションの文章です。
重要なポイントを3〜5個に要約し、HTML形式の箇条書きで出力してください。

ルール:
- 出力は <ul><li>...</li></ul> 形式のHTMLのみ（他の説明文不要）
- 各項目は1文で簡潔に
- 具体的な数値（売上高、利益、増減率など）があれば必ず含める
- 業績の良し悪しが分かる表現を使う

文章:
{comment_text}"""

        # 複数モデルを試行（クオータ制限対応）
        response = None
        for model_name in ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-2.0-flash-lite"]:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                if response and response.text:
                    break
            except Exception:
                continue

        if response and response.text:
            result = response.text.strip()
            # <ul>タグが含まれていることを確認
            if "<ul>" in result and "<li>" in result:
                # 余計なmarkdownコードブロックを除去
                result = re.sub(r'```html?\s*', '', result)
                result = re.sub(r'```\s*', '', result)
                return result.strip()
            # タグがない場合、テキストからHTML生成
            lines = [l.strip() for l in result.split('\n') if l.strip()]
            items = []
            for line in lines:
                # 「・」「-」「•」などの箇条書き記号を除去
                line = re.sub(r'^[・\-•\*]\s*', '', line)
                if line:
                    items.append(f"<li>{line}</li>")
            if items:
                return f"<ul>{''.join(items)}</ul>"

        return ""

    except Exception as e:
        print(f"Gemini API error: {e}")
        return ""


def summarize_with_claude(comment_text: str, section_name: str) -> str:
    """
    Claude APIでコメントを要約

    Args:
        comment_text: 要約対象のテキスト
        section_name: セクション名

    Returns:
        要約テキスト（失敗時は空文字列）
    """
    try:
        import anthropic
    except ImportError:
        return ""

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return ""

    if not comment_text or len(comment_text.strip()) < 50:
        return ""

    try:
        client = anthropic.Anthropic(api_key=api_key)

        message = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": f"""以下の{section_name}に関する文章を、重要なポイントを3-5個の箇条書きにまとめてください。

{comment_text}

重要なポイントのみを、簡潔な箇条書きで要約してください。各項目は1-2文程度にしてください。"""
            }]
        )

        if message.content and len(message.content) > 0:
            return message.content[0].text
        return ""

    except Exception:
        return ""


# --- ローカル要約（フォールバック用） ---

IMPORTANCE_KEYWORDS = {
    '増収': 3, '減収': 3, '増益': 3, '減益': 3,
    '増加': 2, '減少': 2, '成長': 3, '回復': 3,
    '悪化': 3, '改善': 3, '過去最高': 4, '前年比': 3,
    '計画': 2, '見通し': 3, '予想': 3, '見込': 2,
    '拡大': 2, '縮小': 2, '好調': 3, '堅調': 2,
    '上回': 3, '下回': 3, '達成': 3, '超過': 3,
}

SENTENCE_START_KEYWORDS = [
    '当社', '当期', '今後', '来期', '次期',
    '当連結', '当グループ', 'この結果',
    '以上の結果', '通期', '上半期', '下半期',
]

NUMBER_PATTERNS = [
    r'\d+[,，]\d+百万円',
    r'\d+[,，]\d+億円',
    r'\d+[,，]\d+千万円',
    r'\d+\.?\d*[%％]',
    r'前年[同期]*比\s*\d+',
    r'\d+[,，]?\d*百万円',
    r'\d+[,，]?\d*億円',
]


def _score_sentence(sentence: str, index: int, total: int) -> float:
    score = 0.0
    for keyword, weight in IMPORTANCE_KEYWORDS.items():
        if keyword in sentence:
            score += weight
    for kw in SENTENCE_START_KEYWORDS:
        if sentence.strip().startswith(kw):
            score += 2
            break
    for pattern in NUMBER_PATTERNS:
        if re.search(pattern, sentence):
            score += 3
            break
    if len(sentence.strip()) < 20:
        score -= 5
    if len(sentence.strip()) < 40 and not re.search(r'[。、]', sentence):
        score -= 3
    return score


def summarize_text_local(text: str, section_name: str, max_sentences: int = 5) -> str:
    """ローカルキーワードベースでテキストを要約する（フォールバック用）"""
    if not text or len(text.strip()) < 50:
        return f"{section_name}のテキストが短すぎるため要約できません。"

    raw = text.split('。')
    sentences = [s.strip() + '。' for s in raw if s.strip() and len(s.strip()) > 10]
    if not sentences:
        return f"{section_name}の文を抽出できませんでした。"

    scored: List[Tuple[int, float, str]] = []
    for i, sent in enumerate(sentences):
        score = _score_sentence(sent, i, len(sentences))
        scored.append((i, score, sent))

    min_s = min(3, len(scored))
    scored_sorted = sorted(scored, key=lambda x: x[1], reverse=True)
    top = scored_sorted[:max(min_s, min(max_sentences, len(scored_sorted)))]
    top_ordered = sorted(top, key=lambda x: x[0])

    items = []
    for _, _, sent in top_ordered:
        clean = re.sub(r'\s+', '', sent).strip()
        if clean:
            items.append(f"<li>{clean}</li>")

    if not items:
        return f"{section_name}の要約を生成できませんでした。"

    return f"<ul>{''.join(items)}</ul>"


def summarize_company_comments(comments: Dict[str, str]) -> Dict[str, any]:
    """
    会社コメントの要約

    フォールバック順序:
    1. GEMINI_API_KEY あり → Gemini APIで要約（無料）
    2. ANTHROPIC_API_KEY あり → Claude APIで要約
    3. どちらもなし → ローカルキーワードベース要約
    """
    if not comments:
        return {
            "has_summaries": False,
            "message": "会社コメントが抽出されていません。"
        }

    result = {"has_summaries": False}

    section_map = {
        'management_discussion': ('management_summary', '経営成績'),
        'future_outlook': ('outlook_summary', '今後の見通し'),
    }

    for comment_key, (result_key, section_name) in section_map.items():
        text = comments.get(comment_key)
        if not text:
            continue

        summary = ""

        # 1. Gemini API（無料枠）を試行
        if not summary:
            summary = summarize_with_gemini(text, section_name)

        # 2. Claude APIを試行
        if not summary:
            summary = summarize_with_claude(text, section_name)

        # 3. ローカル要約（最終フォールバック）
        if not summary:
            summary = summarize_text_local(text, section_name)

        if summary:
            result[result_key] = summary
            result["has_summaries"] = True

    if not result["has_summaries"]:
        result["message"] = "要約可能なコメントが見つかりませんでした。"

    return result


def summarize_text_simple(text: str, max_length: int = 300) -> str:
    """シンプルなテキスト要約（後方互換性のために残す）"""
    if not text:
        return ""
    sentences = text.split('。')
    summary = ""
    for sentence in sentences:
        if len(summary) + len(sentence) < max_length:
            summary += sentence + "。"
        else:
            break
    if len(summary) > max_length:
        summary = summary[:max_length] + "..."
    return summary.strip()


if __name__ == "__main__":
    # .envを読み込み
    try:
        from dotenv import load_dotenv
        from pathlib import Path
        env_path = Path(__file__).resolve().parent.parent.parent / '.env'
        load_dotenv(env_path)
    except ImportError:
        pass

    test_comments = {
        "management_discussion": """
        当連結会計年度における我が国経済は、新型コロナウイルス感染症の影響が徐々に緩和される中、
        企業活動の正常化が進み、景気は緩やかな回復基調となりました。
        一方で、原材料価格の高騰や為替の変動など、先行き不透明な状況が続いています。
        このような環境下、当社グループは中期経営計画に基づき、デジタルトランスフォーメーションの推進、
        新規事業の創出、業務効率化などに取り組んでまいりました。
        この結果、売上高は前年比15.3%増の1,234,567百万円となり、過去最高を更新しました。
        営業利益は前年比8.2%増の123,456百万円となり、増収増益を達成しました。
        """,
        "future_outlook": """
        今後の見通しにつきましては、国内外の経済情勢は依然として不透明な状況が続くと予想されます。
        このような状況下、当社グループは引き続き成長戦略を推進し、収益力の向上に努めてまいります。
        特に、DX推進による業務効率化、新規事業の拡大、海外展開の加速を重点施策として取り組む予定です。
        来期の連結業績予想は、売上高1,350,000百万円（前年比9.3%増）を見込んでおります。
        """
    }

    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    print("=== コメント要約テスト ===")
    print(f"GEMINI_API_KEY: {'設定済み' if os.environ.get('GEMINI_API_KEY') else '未設定'}")
    result = summarize_company_comments(test_comments)

    if result.get("has_summaries"):
        if result.get("management_summary"):
            print("\n【経営成績の要約】")
            print(result["management_summary"])
        if result.get("outlook_summary"):
            print("\n【今後の見通しの要約】")
            print(result["outlook_summary"])
    else:
        print(result.get("message", "要約できませんでした。"))
