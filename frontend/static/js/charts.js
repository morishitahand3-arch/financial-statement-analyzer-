// 分析結果を取得して表示
document.addEventListener('DOMContentLoaded', async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const filename = urlParams.get('file');

    if (!filename) {
        alert('ファイル名が指定されていません');
        window.location.href = '/';
        return;
    }

    try {
        const response = await fetch(`/api/analyze/${filename}`);

        // レスポンスがJSONかチェック
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            alert('サーバーからの応答が不正です。PDFの解析に時間がかかりすぎた可能性があります。\n小さいサイズのPDFで再度お試しください。');
            window.location.href = '/upload';
            return;
        }

        const data = await response.json();

        if (response.ok) {
            displayResults(data);
        } else {
            alert(data.error || '分析結果の取得に失敗しました');
            window.location.href = '/upload';
        }
    } catch (error) {
        alert('分析中にエラーが発生しました。\nPDFのサイズが大きすぎる可能性があります。\n\n' + error.message);
        window.location.href = '/upload';
    }
});

// 結果を表示
function displayResults(data) {
    // 企業情報を表示
    const companyInfo = document.getElementById('companyInfo');
    companyInfo.textContent = `会社名: ${data.company_name || '不明'} | 会計年度: ${data.fiscal_year || '不明'}`;

    // 収益性分析の結果を表示
    const profitability = data.results.profitability;
    document.getElementById('roe').textContent =
        profitability.roe !== null ? `${profitability.roe}%` : 'データなし';
    document.getElementById('roa').textContent =
        profitability.roa !== null ? `${profitability.roa}%` : 'データなし';
    document.getElementById('operatingMargin').textContent =
        profitability.operating_margin !== null ? `${profitability.operating_margin}%` : 'データなし';

    // 安全性分析の結果を表示
    const safety = data.results.safety;
    document.getElementById('equityRatio').textContent =
        safety.equity_ratio !== null ? `${safety.equity_ratio}%` : 'データなし';
    document.getElementById('currentRatio').textContent =
        safety.current_ratio !== null ? `${safety.current_ratio}%` : 'データなし';
    document.getElementById('fixedRatio').textContent =
        safety.fixed_ratio !== null ? `${safety.fixed_ratio}%` : 'データなし';

    // コメント表示
    const profitabilityComments = document.getElementById('profitabilityComments');
    if (profitability.comments && profitability.comments.length > 0) {
        profitabilityComments.innerHTML = '<ul>' +
            profitability.comments.map(c => `<li>${c}</li>`).join('') +
            '</ul>';
    } else {
        profitabilityComments.innerHTML = '<p>評価コメントはありません</p>';
    }

    const safetyComments = document.getElementById('safetyComments');
    if (safety.comments && safety.comments.length > 0) {
        safetyComments.innerHTML = '<ul>' +
            safety.comments.map(c => `<li>${c}</li>`).join('') +
            '</ul>';
    } else {
        safetyComments.innerHTML = '<p>評価コメントはありません</p>';
    }

    // KPIを表示
    displayKPIs(data);

    // 業績予想比較を表示
    displayForecastComparison(data);

    // 成長性分析を表示
    displayGrowthAnalysis(data);

    // 経営陣コメントを表示
    displayCompanyComments(data);

    // 業績予想修正を表示
    displayForecastRevisions(data);

    // グラフを描画（実データを使用）
    createChart(profitability, safety);

    // 財務諸表チャートを初期化
    if (typeof initializeFinancialCharts === 'function') {
        initializeFinancialCharts(data);
    }
}

// グラフを作成
function createChart(profitability, safety) {
    const ctx = document.getElementById('metricsChart').getContext('2d');

    // 実際のデータを使用（nullの場合は0）
    const chartData = [
        profitability.roe || 0,
        profitability.roa || 0,
        profitability.operating_margin || 0,
        safety.equity_ratio || 0,
        Math.min(safety.current_ratio || 0, 100), // 流動比率は100でキャップ
    ];

    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['ROE', 'ROA', '営業利益率', '自己資本比率', '流動比率'],
            datasets: [{
                label: '財務指標スコア',
                data: chartData,
                backgroundColor: 'rgba(102, 126, 234, 0.25)',
                borderColor: 'rgba(102, 126, 234, 1)',
                borderWidth: 3,
                pointBackgroundColor: 'rgba(102, 126, 234, 1)',
                pointBorderColor: '#fff',
                pointBorderWidth: 3,
                pointRadius: 6,
                pointHoverRadius: 8,
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(102, 126, 234, 1)',
                pointHoverBorderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 1200,
                easing: 'easeOutQuart'
            },
            interaction: {
                mode: 'index',
                intersect: false
            },
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    angleLines: {
                        color: 'rgba(160, 174, 192, 0.2)',
                        lineWidth: 1
                    },
                    grid: {
                        color: 'rgba(160, 174, 192, 0.15)',
                        circular: true,
                        lineWidth: 1
                    },
                    pointLabels: {
                        font: {
                            size: 14,
                            weight: '600',
                            family: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
                        },
                        color: '#2d3748',
                        padding: 15
                    },
                    ticks: {
                        stepSize: 20,
                        backdropColor: 'rgba(255, 255, 255, 0.9)',
                        backdropPadding: 4,
                        font: {
                            size: 12,
                            weight: '500',
                            family: "'Inter', sans-serif"
                        },
                        color: '#718096',
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        padding: 20,
                        font: {
                            size: 14,
                            weight: '600',
                            family: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
                        },
                        color: '#2d3748',
                        usePointStyle: true,
                        pointStyle: 'circle',
                        boxWidth: 10,
                        boxHeight: 10
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(26, 32, 44, 0.95)',
                    titleFont: {
                        size: 15,
                        weight: '600',
                        family: "'Inter', sans-serif"
                    },
                    bodyFont: {
                        size: 14,
                        weight: '400',
                        family: "'Inter', sans-serif"
                    },
                    padding: 16,
                    cornerRadius: 12,
                    displayColors: true,
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            return context.label + ': ' + context.parsed.r.toFixed(2) + '%';
                        }
                    }
                }
            }
        }
    });
}

// KPIを表示
function displayKPIs(data) {
    const keyMetrics = data.results.key_metrics;

    if (keyMetrics) {
        // 売上高
        document.getElementById('revenueKpi').textContent =
            formatCurrency(keyMetrics.revenue.current);

        if (keyMetrics.revenue.previous) {
            document.getElementById('revenuePrevious').textContent =
                `前期: ${formatCurrency(keyMetrics.revenue.previous)}`;
            document.getElementById('revenueGrowth').innerHTML =
                formatGrowthRate(keyMetrics.revenue.growth_rate);
        }

        // 営業利益
        document.getElementById('operatingIncomeKpi').textContent =
            formatCurrency(keyMetrics.operating_income.current);

        if (keyMetrics.operating_income.previous) {
            document.getElementById('operatingIncomePrevious').textContent =
                `前期: ${formatCurrency(keyMetrics.operating_income.previous)}`;
            document.getElementById('operatingIncomeGrowth').innerHTML =
                formatGrowthRate(keyMetrics.operating_income.growth_rate);
        }

        // 当期純利益
        document.getElementById('netIncomeKpi').textContent =
            formatCurrency(keyMetrics.net_income.current);

        if (keyMetrics.net_income.previous) {
            document.getElementById('netIncomePrevious').textContent =
                `前期: ${formatCurrency(keyMetrics.net_income.previous)}`;
            document.getElementById('netIncomeGrowth').innerHTML =
                formatGrowthRate(keyMetrics.net_income.growth_rate);
        }
    }
}

// 業績予想比較を表示
function displayForecastComparison(data) {
    const forecast = data.results.forecast_comparison;

    if (forecast && forecast.has_forecast) {
        document.getElementById('forecastSection').style.display = 'block';

        // 売上高
        if (forecast.revenue) {
            document.getElementById('revenueActual').textContent =
                formatCurrency(forecast.revenue.actual);
            document.getElementById('revenueForecast').textContent =
                formatCurrency(forecast.revenue.forecast);
            document.getElementById('revenueAchievement').textContent =
                forecast.revenue.achievement_rate ? `${forecast.revenue.achievement_rate.toFixed(1)}%` : '-';
            document.getElementById('revenueForecastComment').textContent =
                forecast.revenue.evaluation.comment;
            document.getElementById('revenueForecastCard').className =
                'forecast-card ' + forecast.revenue.evaluation.color_class;
        }

        // 営業利益
        if (forecast.operating_income) {
            document.getElementById('operatingIncomeActual').textContent =
                formatCurrency(forecast.operating_income.actual);
            document.getElementById('operatingIncomeForecast').textContent =
                formatCurrency(forecast.operating_income.forecast);
            document.getElementById('operatingIncomeAchievement').textContent =
                forecast.operating_income.achievement_rate ? `${forecast.operating_income.achievement_rate.toFixed(1)}%` : '-';
            document.getElementById('operatingIncomeForecastComment').textContent =
                forecast.operating_income.evaluation.comment;
            document.getElementById('operatingIncomeForecastCard').className =
                'forecast-card ' + forecast.operating_income.evaluation.color_class;
        }

        // 当期純利益
        if (forecast.net_income) {
            document.getElementById('netIncomeActual').textContent =
                formatCurrency(forecast.net_income.actual);
            document.getElementById('netIncomeForecast').textContent =
                formatCurrency(forecast.net_income.forecast);
            document.getElementById('netIncomeAchievement').textContent =
                forecast.net_income.achievement_rate ? `${forecast.net_income.achievement_rate.toFixed(1)}%` : '-';
            document.getElementById('netIncomeForecastComment').textContent =
                forecast.net_income.evaluation.comment;
            document.getElementById('netIncomeForecastCard').className =
                'forecast-card ' + forecast.net_income.evaluation.color_class;
        }

        // 総合評価
        if (forecast.overall_evaluation) {
            document.getElementById('forecastOverallEval').textContent =
                forecast.overall_evaluation;
        }
    }
}

// 成長性分析を表示
function displayGrowthAnalysis(data) {
    const growth = data.results.growth;

    if (growth && growth.has_comparison) {
        document.getElementById('growthSection').style.display = 'block';

        // 成長率を表示
        document.getElementById('revenueGrowthRate').innerHTML =
            formatGrowthRateWithArrow(growth.revenue_growth);
        document.getElementById('operatingIncomeGrowthRate').innerHTML =
            formatGrowthRateWithArrow(growth.operating_income_growth);
        document.getElementById('netIncomeGrowthRate').innerHTML =
            formatGrowthRateWithArrow(growth.net_income_growth);

        // コメントを表示
        const commentsEl = document.getElementById('growthComments');
        if (growth.comments && growth.comments.length > 0) {
            commentsEl.innerHTML = growth.comments.map(c => `<li>${c}</li>`).join('');
        }

        // 総合評価を表示
        if (growth.overall_evaluation) {
            document.getElementById('growthOverallEval').textContent =
                growth.overall_evaluation;
        }
    }
}

// 経営陣コメントを表示
function displayCompanyComments(data) {
    const comments = data.results.company_comments;

    if (comments && comments.has_summaries) {
        document.getElementById('commentsSection').style.display = 'block';

        if (comments.management_summary) {
            document.getElementById('managementBox').style.display = 'block';
            document.getElementById('managementSummary').innerHTML =
                comments.management_summary;
        }

        if (comments.outlook_summary) {
            document.getElementById('outlookBox').style.display = 'block';
            document.getElementById('outlookSummary').innerHTML =
                comments.outlook_summary;
        }
    }
}

// 業績予想修正を表示
function displayForecastRevisions(data) {
    // forecast_comparisonから業績予想データを取得
    const forecastComparison = data.results.forecast_comparison;

    // 業績予想データが存在し、修正履歴がある場合のみ表示
    if (!forecastComparison || !forecastComparison.has_forecast) {
        return;
    }

    // APIレスポンスから修正履歴を取得（ネストされた構造を想定）
    let revisions = null;

    // 複数のパスを試行
    if (data.results.forecast_comparison && data.results.forecast_comparison.revisions) {
        revisions = data.results.forecast_comparison.revisions;
    }

    if (!revisions || revisions.length === 0) {
        return;
    }

    // セクションを表示
    document.getElementById('forecastRevisionSection').style.display = 'block';

    // 修正履歴のHTMLを生成
    const revisionContent = document.getElementById('forecastRevisionContent');
    let html = '';

    revisions.forEach((revision, index) => {
        html += `
            <div class="revision-card">
                <h3>修正 ${index + 1}</h3>
                ${revision.revision_date ? `<p class="revision-date">修正日: ${revision.revision_date}</p>` : ''}

                <table class="revision-table">
                    <thead>
                        <tr>
                            <th>項目</th>
                            <th>修正前</th>
                            <th>修正後</th>
                            <th>変化率</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${generateRevisionRow(
                            '売上高',
                            revision.previous_revenue,
                            revision.revised_revenue
                        )}
                        ${generateRevisionRow(
                            '営業利益',
                            revision.previous_operating_income,
                            revision.revised_operating_income
                        )}
                        ${generateRevisionRow(
                            '当期純利益',
                            revision.previous_net_income,
                            revision.revised_net_income
                        )}
                    </tbody>
                </table>

                ${revision.reason ? `
                    <div class="revision-reason">
                        <h4>修正理由</h4>
                        <p>${revision.reason}</p>
                    </div>
                ` : ''}
            </div>
        `;
    });

    revisionContent.innerHTML = html;
}

// 業績予想修正テーブルの行を生成
function generateRevisionRow(label, previousValue, revisedValue) {
    if (!previousValue && !revisedValue) {
        return '';
    }

    const changeRate = calculateChangeRate(previousValue, revisedValue);
    const changeClass = changeRate > 0 ? 'positive' : changeRate < 0 ? 'negative' : 'neutral';

    return `
        <tr>
            <td>${label}</td>
            <td>${formatCurrency(previousValue)}</td>
            <td>${formatCurrency(revisedValue)}</td>
            <td class="${changeClass}">${formatChangeRate(changeRate)}</td>
        </tr>
    `;
}

// 変化率を計算
function calculateChangeRate(previous, revised) {
    if (!previous || previous === 0) return 0;
    return ((revised - previous) / previous) * 100;
}

// 変化率をフォーマット
function formatChangeRate(rate) {
    if (rate === 0) return '変更なし';
    const sign = rate > 0 ? '+' : '';
    return `${sign}${rate.toFixed(1)}%`;
}

// ユーティリティ関数: 通貨フォーマット
function formatCurrency(value) {
    if (value === null || value === undefined) return '-';
    // 値は既に百万円単位なので、カンマ区切りで表示
    return `${value.toLocaleString('ja-JP', {maximumFractionDigits: 0})}百万円`;
}

// ユーティリティ関数: 成長率フォーマット（矢印なし）
function formatGrowthRate(rate) {
    if (rate === null || rate === undefined) return '';
    const arrow = rate >= 0 ? '↑' : '↓';
    const colorClass = rate >= 0 ? 'growth-positive' : 'growth-negative';
    return `<span class="${colorClass}">${arrow} ${Math.abs(rate).toFixed(1)}%</span>`;
}

// ユーティリティ関数: 成長率フォーマット（矢印付き大きめ表示）
function formatGrowthRateWithArrow(rate) {
    if (rate === null || rate === undefined) return '<span>-</span>';
    const arrow = rate >= 0 ? '↑' : '↓';
    const colorClass = rate >= 0 ? 'growth-positive' : 'growth-negative';
    return `<span class="${colorClass}">${arrow} ${rate.toFixed(1)}%</span>`;
}
