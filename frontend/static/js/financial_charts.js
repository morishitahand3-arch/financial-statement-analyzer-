/**
 * 財務諸表可視化モジュール
 * BS、PL、CFのチャートを生成する
 */

// タブ切り替え関数
function switchTab(tabName) {
    // すべてのタブコンテンツを非表示
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    // 選択されたタブを表示
    const selectedTab = document.getElementById(`tab-${tabName}`);
    if (selectedTab) {
        selectedTab.classList.add('active');
    }

    // すべてのタブボタンの active クラスを削除
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });

    // クリックされたボタンに active クラスを追加
    event.target.classList.add('active');
}

// BS横積み上げ棒グラフ: 左に資産の部、右に負債・純資産の部
function createBalanceSheetBarChart(balanceSheetData) {
    const canvas = document.getElementById('bsPieChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');

    // 既存のチャートがあれば破棄
    if (window.bsBarChartInstance) {
        window.bsBarChartInstance.destroy();
    }

    // データは既に百万円単位で送られてくるのでそのまま使用
    const currentAssets = balanceSheetData.current_assets || 0;
    const fixedAssets = balanceSheetData.fixed_assets || 0;
    const currentLiabilities = balanceSheetData.current_liabilities || 0;
    const fixedLiabilities = balanceSheetData.fixed_liabilities || 0;
    const netAssets = balanceSheetData.total_net_assets || 0;

    // データの整合性チェック
    const totalAssets = currentAssets + fixedAssets;
    const totalCapital = currentLiabilities + fixedLiabilities + netAssets;

    console.log('=== 貸借対照表データ ===');
    console.log('借方（資産の部）:');
    console.log('  流動資産:', currentAssets.toFixed(2), '百万円');
    console.log('  固定資産:', fixedAssets.toFixed(2), '百万円');
    console.log('  合計:', totalAssets.toFixed(2), '百万円');
    console.log('貸方（負債・純資産の部）:');
    console.log('  流動負債:', currentLiabilities.toFixed(2), '百万円');
    console.log('  固定負債:', fixedLiabilities.toFixed(2), '百万円');
    console.log('  純資産:', netAssets.toFixed(2), '百万円');
    console.log('  合計:', totalCapital.toFixed(2), '百万円');
    console.log('差分:', (totalAssets - totalCapital).toFixed(2), '百万円');

    if (Math.abs(totalAssets - totalCapital) > 0.01) {
        console.warn('警告: 借方と貸方の合計が一致しません！');
    }

    window.bsBarChartInstance = new Chart(ctx, {
        type: 'bar',
        plugins: [ChartDataLabels],
        data: {
            labels: ['借方（資産の部）', '貸方（負債・純資産の部）'],
            datasets: [
                {
                    label: '固定資産',
                    data: [fixedAssets, null],
                    backgroundColor: createGradient(ctx, '#667eea', '#764ba2'),
                    borderColor: 'rgba(102, 126, 234, 1)',
                    borderWidth: 0,
                    borderRadius: 12,
                    hoverBackgroundColor: createGradient(ctx, '#7e92f7', '#8b5fb5'),
                    hoverBorderWidth: 3,
                    hoverBorderColor: 'rgba(102, 126, 234, 1)'
                },
                {
                    label: '流動資産',
                    data: [currentAssets, null],
                    backgroundColor: createGradient(ctx, '#4facfe', '#00f2fe'),
                    borderColor: 'rgba(79, 172, 254, 1)',
                    borderWidth: 0,
                    borderRadius: 12,
                    hoverBackgroundColor: createGradient(ctx, '#5fbdff', '#1ff9ff'),
                    hoverBorderWidth: 3,
                    hoverBorderColor: 'rgba(79, 172, 254, 1)'
                },
                {
                    label: '純資産',
                    data: [null, netAssets],
                    backgroundColor: createGradient(ctx, '#43e97b', '#38f9d7'),
                    borderColor: 'rgba(67, 233, 123, 1)',
                    borderWidth: 0,
                    borderRadius: 12,
                    hoverBackgroundColor: createGradient(ctx, '#54fa8c', '#49ffe8'),
                    hoverBorderWidth: 3,
                    hoverBorderColor: 'rgba(67, 233, 123, 1)'
                },
                {
                    label: '固定負債',
                    data: [null, fixedLiabilities],
                    backgroundColor: createGradient(ctx, '#fa709a', '#fee140'),
                    borderColor: 'rgba(250, 112, 154, 1)',
                    borderWidth: 0,
                    borderRadius: 12,
                    hoverBackgroundColor: createGradient(ctx, '#fb81ab', '#fef251'),
                    hoverBorderWidth: 3,
                    hoverBorderColor: 'rgba(250, 112, 154, 1)'
                },
                {
                    label: '流動負債',
                    data: [null, currentLiabilities],
                    backgroundColor: createGradient(ctx, '#ff9a56', '#ff6a88'),
                    borderColor: 'rgba(255, 154, 86, 1)',
                    borderWidth: 0,
                    borderRadius: 12,
                    hoverBackgroundColor: createGradient(ctx, '#ffab67', '#ff7b99'),
                    hoverBorderWidth: 3,
                    hoverBorderColor: 'rgba(255, 154, 86, 1)'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            animation: {
                duration: 1200,
                easing: 'easeOutQuart'
            },
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                title: {
                    display: true,
                    text: '貸借対照表',
                    font: {
                        size: 24,
                        weight: '700',
                        family: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
                    },
                    padding: { top: 10, bottom: 30 },
                    color: '#1a202c'
                },
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        font: {
                            size: 14,
                            weight: '500',
                            family: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
                        },
                        color: '#4a5568',
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
                            const value = context.parsed.y.toFixed(0);
                            return `${context.dataset.label}: ${Number(value).toLocaleString()}百万円`;
                        },
                        afterLabel: function(context) {
                            const categoryIndex = context.dataIndex;
                            let total = 0;

                            context.chart.data.datasets.forEach((dataset) => {
                                const value = dataset.data[categoryIndex];
                                if (value !== null && value !== undefined) {
                                    total += value;
                                }
                            });

                            const percentage = ((context.parsed.y / total) * 100).toFixed(1);
                            return `構成比: ${percentage}%`;
                        }
                    }
                },
                datalabels: {
                    color: '#ffffff',
                    font: {
                        size: 16,
                        weight: '700',
                        family: "'Inter', sans-serif"
                    },
                    formatter: function(value, context) {
                        if (value === null || value === 0) return '';

                        const categoryIndex = context.dataIndex;
                        let total = 0;
                        context.chart.data.datasets.forEach((dataset) => {
                            const val = dataset.data[categoryIndex];
                            if (val !== null && val !== undefined) {
                                total += val;
                            }
                        });

                        const percentage = ((value / total) * 100).toFixed(1);

                        // パーセンテージのみを表示
                        return `${percentage}%`;
                    },
                    textAlign: 'center',
                    anchor: 'center',
                    align: 'center',
                    textShadowColor: 'rgba(0, 0, 0, 0.5)',
                    textShadowBlur: 4
                }
            },
            scales: {
                x: {
                    stacked: true,
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            size: 14,
                            weight: '600',
                            family: "'Inter', sans-serif"
                        },
                        color: '#2d3748',
                        padding: 10
                    }
                },
                y: {
                    stacked: true,
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: '百万円',
                        font: {
                            size: 15,
                            weight: '600',
                            family: "'Inter', sans-serif"
                        },
                        color: '#2d3748',
                        padding: { bottom: 10 }
                    },
                    grid: {
                        color: 'rgba(160, 174, 192, 0.15)',
                        drawBorder: false,
                        lineWidth: 1
                    },
                    ticks: {
                        font: {
                            size: 13,
                            weight: '500',
                            family: "'Inter', sans-serif"
                        },
                        color: '#718096',
                        padding: 8,
                        callback: function(value) {
                            return value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

// グラデーション作成ヘルパー関数
function createGradient(ctx, color1, color2) {
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, color1);
    gradient.addColorStop(1, color2);
    return gradient;
}

// PL棒グラフ: 売上→利益の流れ
function createIncomeStatementBarChart(incomeStatementData) {
    const canvas = document.getElementById('plBarChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');

    // 既存のチャートがあれば破棄
    if (window.plBarChartInstance) {
        window.plBarChartInstance.destroy();
    }

    // データは既に百万円単位で送られてくるのでそのまま使用
    const revenue = incomeStatementData.revenue || 0;
    const operatingIncome = incomeStatementData.operating_income || 0;
    const netIncome = incomeStatementData.net_income || 0;

    window.plBarChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['売上高', '営業利益', '当期純利益'],
            datasets: [{
                label: '金額（百万円）',
                data: [revenue, operatingIncome, netIncome],
                backgroundColor: [
                    createGradient(ctx, '#667eea', '#764ba2'),
                    createGradient(ctx, '#f093fb', '#f5576c'),
                    createGradient(ctx, '#ffa751', '#ffe259')
                ],
                borderColor: [
                    'rgba(102, 126, 234, 0)',
                    'rgba(245, 87, 108, 0)',
                    'rgba(255, 167, 81, 0)'
                ],
                borderWidth: 0,
                borderRadius: 12,
                hoverBackgroundColor: [
                    createGradient(ctx, '#7e92f7', '#8b5fb5'),
                    createGradient(ctx, '#f7a4fc', '#f6687d'),
                    createGradient(ctx, '#ffb862', '#ffeb6a')
                ],
                hoverBorderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            animation: {
                duration: 1200,
                easing: 'easeOutQuart',
                delay: (context) => {
                    return context.dataIndex * 150;
                }
            },
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                title: {
                    display: true,
                    text: '損益計算書（利益の流れ）',
                    font: {
                        size: 24,
                        weight: '700',
                        family: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
                    },
                    padding: { top: 10, bottom: 30 },
                    color: '#1a202c'
                },
                legend: {
                    display: false
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
                            return `${context.label}: ${Number(context.parsed.y.toFixed(0)).toLocaleString()}百万円`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            size: 14,
                            weight: '600',
                            family: "'Inter', sans-serif"
                        },
                        color: '#2d3748',
                        padding: 10
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: '百万円',
                        font: {
                            size: 15,
                            weight: '600',
                            family: "'Inter', sans-serif"
                        },
                        color: '#2d3748',
                        padding: { bottom: 10 }
                    },
                    grid: {
                        color: 'rgba(160, 174, 192, 0.15)',
                        drawBorder: false,
                        lineWidth: 1
                    },
                    ticks: {
                        font: {
                            size: 13,
                            weight: '500',
                            family: "'Inter', sans-serif"
                        },
                        color: '#718096',
                        padding: 8,
                        callback: function(value) {
                            return value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

// CFグラフ: 3つのキャッシュフロー比較
function createCashFlowBarChart(cashFlowData) {
    const canvas = document.getElementById('cfBarChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');

    // 既存のチャートがあれば破棄
    if (window.cfBarChartInstance) {
        window.cfBarChartInstance.destroy();
    }

    // データは既に百万円単位で送られてくるのでそのまま使用
    const operatingCF = cashFlowData.operating_cash_flow || 0;
    const investingCF = cashFlowData.investing_cash_flow || 0;
    const financingCF = cashFlowData.financing_cash_flow || 0;

    // 各CFの色を決定（プラスはグリーングラデーション、マイナスはレッドグラデーション）
    const colors = [operatingCF, investingCF, financingCF].map(value =>
        value >= 0 ? createGradient(ctx, '#43e97b', '#38f9d7') : createGradient(ctx, '#f093fb', '#f5576c')
    );

    const hoverColors = [operatingCF, investingCF, financingCF].map(value =>
        value >= 0 ? createGradient(ctx, '#54fa8c', '#49ffe8') : createGradient(ctx, '#f7a4fc', '#f6687d')
    );

    window.cfBarChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['営業CF', '投資CF', '財務CF'],
            datasets: [{
                label: 'キャッシュフロー（百万円）',
                data: [operatingCF, investingCF, financingCF],
                backgroundColor: colors,
                borderColor: 'transparent',
                borderWidth: 0,
                borderRadius: 12,
                hoverBackgroundColor: hoverColors,
                hoverBorderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            animation: {
                duration: 1200,
                easing: 'easeOutQuart',
                delay: (context) => {
                    return context.dataIndex * 150;
                }
            },
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                title: {
                    display: true,
                    text: 'キャッシュフロー計算書',
                    font: {
                        size: 24,
                        weight: '700',
                        family: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
                    },
                    padding: { top: 10, bottom: 30 },
                    color: '#1a202c'
                },
                legend: {
                    display: false
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
                            const value = context.parsed.y.toFixed(0);
                            const sign = context.parsed.y >= 0 ? '+' : '';
                            return `${context.label}: ${sign}${Number(value).toLocaleString()}百万円`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            size: 14,
                            weight: '600',
                            family: "'Inter', sans-serif"
                        },
                        color: '#2d3748',
                        padding: 10
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: '百万円',
                        font: {
                            size: 15,
                            weight: '600',
                            family: "'Inter', sans-serif"
                        },
                        color: '#2d3748',
                        padding: { bottom: 10 }
                    },
                    grid: {
                        color: 'rgba(160, 174, 192, 0.15)',
                        drawBorder: false,
                        lineWidth: 1
                    },
                    ticks: {
                        font: {
                            size: 13,
                            weight: '500',
                            family: "'Inter', sans-serif"
                        },
                        color: '#718096',
                        padding: 8,
                        callback: function(value) {
                            const sign = value >= 0 ? '+' : '';
                            return sign + value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

// セグメント円グラフ: セグメント別売上構成比
function createSegmentPieChart(segmentData) {
    const canvas = document.getElementById('segmentPieChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');

    // 既存のチャートがあれば破棄
    if (window.segmentPieChartInstance) {
        window.segmentPieChartInstance.destroy();
    }

    const labels = segmentData.segments.map(seg => seg.name);
    const data = segmentData.segments.map(seg => seg.revenue / 1000000);

    // カラーパレット
    const colors = [
        'rgba(102, 126, 234, 0.8)',
        'rgba(118, 75, 162, 0.8)',
        'rgba(253, 126, 20, 0.8)',
        'rgba(40, 167, 69, 0.8)',
        'rgba(220, 53, 69, 0.8)',
        'rgba(23, 162, 184, 0.8)'
    ];

    window.segmentPieChartInstance = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors.slice(0, labels.length),
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                title: {
                    display: true,
                    text: 'セグメント別売上構成比',
                    font: {
                        size: 18
                    }
                },
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.parsed.toFixed(0);
                            const percentage = context.label.includes('%') ?
                                '' : ` (${((context.parsed / data.reduce((a, b) => a + b, 0)) * 100).toFixed(1)}%)`;
                            return `${context.label}: ${value}百万円${percentage}`;
                        }
                    }
                }
            }
        }
    });
}

// セグメント営業利益率の棒グラフ
function createSegmentMarginChart(segmentData) {
    const canvas = document.getElementById('segmentMarginChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');

    // 既存のチャートがあれば破棄
    if (window.segmentMarginChartInstance) {
        window.segmentMarginChartInstance.destroy();
    }

    // 営業利益率データがあるセグメントのみ
    const segmentsWithMargin = segmentData.segments.filter(seg => seg.margin !== null);

    if (segmentsWithMargin.length === 0) {
        // データがない場合はチャートを表示しない
        return;
    }

    const labels = segmentsWithMargin.map(seg => seg.name);
    const margins = segmentsWithMargin.map(seg => seg.margin);

    window.segmentMarginChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: '営業利益率（%）',
                data: margins,
                backgroundColor: 'rgba(102, 126, 234, 0.8)',
                borderColor: 'rgba(102, 126, 234, 1)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                title: {
                    display: true,
                    text: 'セグメント別営業利益率',
                    font: {
                        size: 18
                    }
                },
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `営業利益率: ${context.parsed.y.toFixed(1)}%`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: '営業利益率（%）'
                    }
                }
            }
        }
    });
}

// データがロードされた後にチャートを初期化
// charts.jsのdisplayResults関数から呼び出される
function initializeFinancialCharts(data) {
    // 貸借対照表データがあればBSチャートを作成
    if (data.results.safety) {
        const balanceSheetData = {
            current_assets: data.results.safety.current_assets || 0,
            fixed_assets: data.results.safety.fixed_assets || 0,
            current_liabilities: data.results.safety.current_liabilities || 0,
            fixed_liabilities: data.results.safety.fixed_liabilities || 0,
            total_net_assets: data.results.safety.total_net_assets || 0
        };

        // 資産または負債・純資産のデータがある場合のみチャートを作成
        if (balanceSheetData.current_assets > 0 || balanceSheetData.fixed_assets > 0) {
            createBalanceSheetBarChart(balanceSheetData);
        }
    }

    // 損益計算書データがあればPLチャートを作成
    if (data.results.key_metrics) {
        const incomeStatementData = {
            revenue: data.results.key_metrics.revenue?.current || 0,
            operating_income: data.results.key_metrics.operating_income?.current || 0,
            net_income: data.results.key_metrics.net_income?.current || 0
        };

        // 売上高データがある場合のみチャートを作成
        if (incomeStatementData.revenue > 0) {
            createIncomeStatementBarChart(incomeStatementData);
        }
    }

    // キャッシュフローデータがあればCFチャートを作成
    if (data.results.cash_flow && data.results.cash_flow.data) {
        createCashFlowBarChart(data.results.cash_flow.data);
        // CFタブボタンを表示
        const cfTabButton = document.getElementById('cfTabButton');
        if (cfTabButton) {
            cfTabButton.style.display = 'inline-block';
        }
    }

    // セグメントデータがあればセグメントチャートを作成
    if (data.results.segment_analysis && data.results.segment_analysis.has_segments) {
        // セグメントチャート用のコンテナがあれば作成
        if (document.getElementById('segmentPieChart')) {
            createSegmentPieChart(data.results.segment_analysis);
        }
        if (document.getElementById('segmentMarginChart')) {
            createSegmentMarginChart(data.results.segment_analysis);
        }
    }
}

// グローバルスコープに関数を追加
window.switchTab = switchTab;
window.createBalanceSheetBarChart = createBalanceSheetBarChart;
window.createIncomeStatementBarChart = createIncomeStatementBarChart;
window.createCashFlowBarChart = createCashFlowBarChart;
window.createSegmentPieChart = createSegmentPieChart;
window.createSegmentMarginChart = createSegmentMarginChart;
window.initializeFinancialCharts = initializeFinancialCharts;
