<template>
  <div class="orders-container">
    <div class="header">
      <h2>资产看板</h2>
      <div class="header-actions">
        <div class="action-buttons">
          <el-button 
            :type="currentMode === 'reseller' ? 'success' : 'info'"
            @click="toggleMode"
          >
            {{ currentMode === 'reseller' ? '收藏家模式' : '倒狗模式' }}
          </el-button>
        </div>
        <div class="user-info">
          <span v-if="userStore.isAuthenticated">当前用户：</span>
          <span v-if="userStore.isAuthenticated" class="username" @click="$router.push('/profile')" style="cursor: pointer; color: #2196F3; text-decoration: underline;">{{ userStore.currentUser?.username }}</span>
          <button v-if="userStore.isAuthenticated" class="btn btn-logout" @click="logout">退出</button>
        </div>
      </div>
    </div>

    <!-- 倒狗模式内容 -->
    <div v-if="currentMode === 'reseller'">
      <!-- 倒狗模式操作栏 -->
      <div class="reseller-actions">
        <div class="view-tabs">
          <el-button 
            v-for="tab in viewTabs" 
            :key="tab.value"
            :class="{ active: activeView === tab.value }"
            @click="activeView = tab.value"
          >
            {{ tab.label }}
          </el-button>
        </div>
        <div class="action-buttons">
          <!-- 资产版块按钮 -->
          <template v-if="activeView === 'asset'">
            <el-button type="info" @click="showAnnualLimitDialog">
              <el-icon><Money /></el-icon> 年度手办消费上限
            </el-button>
            <el-button type="primary" @click="refreshData">
              <el-icon><Refresh /></el-icon> 刷新资产
            </el-button>
          </template>
          <!-- 行情版块按钮 -->
          <template v-if="activeView === 'market'">
            <el-button type="primary" @click="refreshData">
              <el-icon><Refresh /></el-icon> 刷新行情
            </el-button>
            <el-button @click="openAlertSettings">
              <el-icon><Bell /></el-icon> 设置预警
            </el-button>
          </template>
          <!-- 交易版块按钮 -->
          <template v-if="activeView === 'trade'">
            <el-button type="primary" @click="exportBill">
              <el-icon><Download /></el-icon> 账单导出
            </el-button>
            <el-button type="primary" @click="refreshTradeData">
              <el-icon><Refresh /></el-icon> 刷新交易
            </el-button>
          </template>
        </div>
      </div>

      <!-- 资产视图 -->
      <div v-if="activeView === 'asset'">
        <!-- 资产概览区 -->
        <div class="asset-overview">
          <div class="overview-item">
            <span class="label">总资产:</span>
            <span class="value">¥{{ formatNumber(dashboardData?.summary?.total_assets || 128500) }}</span>
          </div>
          <div class="overview-item">
            <span class="label">日涨跌:</span>
            <span 
              class="value" 
              :class="{ 
                positive: dashboardData?.summary?.has_daily_change && dashboardData?.summary?.daily_change >= 0, 
                negative: dashboardData?.summary?.has_daily_change && dashboardData?.summary?.daily_change < 0 
              }"
            >
              <template v-if="dashboardData?.summary?.has_daily_change">
                {{ dashboardData?.summary?.daily_change >= 0 ? '+' : '' }}¥{{ formatNumber(Math.abs(dashboardData?.summary?.daily_change || 0)) }}({{ dashboardData?.summary?.daily_change >= 0 ? '+' : '' }}{{ (dashboardData?.summary?.daily_change_percentage || 0).toFixed(2) }}%)
              </template>
              <template v-else>
                -- (--%)
              </template>
            </span>
          </div>
          <div class="overview-item">
            <span class="label">仓位:</span>
            <span 
              class="value position-value"
              :class="'position-' + (dashboardData?.summary?.position_color || 'red')"
            >
              {{ dashboardData?.summary?.position || '满仓' }}
              <template v-if="dashboardData?.summary?.position_percentage !== undefined">
                ({{ dashboardData?.summary?.position_percentage }}%)
              </template>
            </span>
          </div>
        </div>

        <div class="divider"></div>

        <!-- 指数对比 -->
        <div class="index-comparison">
          <div class="index-item">
            <span class="label">上证指数:</span>
            <span class="value">{{ dashboardData?.summary?.sh_index || 3200 }}</span>
          </div>
          <div class="index-item">
            <span class="label">你的塑料指数:</span>
            <span class="value">{{ dashboardData?.summary?.plastic_index || 2847 }}</span>
          </div>
          <div class="index-item">
            
            <span 
              class="value" 
              :class="{
                positive: (dashboardData?.summary?.outperform_percentage || 0) > 0,
                negative: (dashboardData?.summary?.outperform_percentage || 0) < 0,
                neutral: (dashboardData?.summary?.outperform_percentage || 0) === 0
              }"
            >
              <template v-if="(dashboardData?.summary?.outperform_percentage || 0) > 0">
                🟢 跑赢大盘+{{ dashboardData?.summary?.outperform_percentage }}% ↑
              </template>
              <template v-else-if="(dashboardData?.summary?.outperform_percentage || 0) < 0">
                🔴 跑输大盘{{ dashboardData?.summary?.outperform_percentage }}% ↓
              </template>
              <template v-else>
                ➖ 持平
              </template>
            </span>
          </div>
        </div>

        <!-- 资产分布和收益曲线 -->
        <div class="chart-section">
          <div class="chart-item">
            <div class="section-title">资产分布饼图</div>
            <div ref="pieChart" class="pie-chart"></div>
          </div>
          <div class="chart-item">
            <div class="section-title">收益曲线(近1月)</div>
            <div ref="profitChart" class="profit-chart"></div>
          </div>
        </div>

        <!-- 盈亏分析 -->
        <div class="profit-analysis">
          <div class="section-title">盈亏分析</div>
          <div class="analysis-grid">
            <div class="analysis-item">
              <div class="analysis-label">浮动盈亏</div>
              <div class="analysis-value positive">+¥{{ formatNumber(dashboardData?.profit?.floating || 23400) }}</div>
              <div class="analysis-desc">(未卖出)</div>
            </div>
            <div class="analysis-item">
              <div class="analysis-label">实现盈亏</div>
              <div class="analysis-value positive">+¥{{ formatNumber(dashboardData?.profit?.realized || 8200) }}</div>
              <div class="analysis-desc">(已转卖)</div>
            </div>
            <div class="analysis-item">
              <div class="analysis-label">总收益率</div>
              <div class="analysis-value positive">+{{ dashboardData?.profit?.total_rate || 24.6 }}%</div>
              <div class="analysis-desc">(年化31%)</div>
            </div>
          </div>
        </div>

        <!-- 持仓列表 -->
        <div class="holdings-section">
          <div class="section-header">
            <div class="section-title">
              📊 持仓列表 (按盈亏排序)
              <el-tooltip
                placement="top"
                :show-after="200"
                effect="light"
              >
                <template #content>
                  <div v-html="statusTable"></div>
                </template>
                <el-button size="small" type="info" class="status-help-button">
                  ?
                </el-button>
              </el-tooltip>
            </div>
            <el-button @click="showFilter = !showFilter">
              筛选 ▼
            </el-button>
          </div>
          
          <!-- 筛选条件 -->
          <div v-if="showFilter" class="filter-section">
            <div class="filter-row">
              <el-input placeholder="搜索" prefix-icon="el-icon-search" class="search-input"></el-input>
              <el-button 
                v-for="filter in holdingFilters" 
                :key="filter.value"
                :class="{ active: selectedHoldingFilter === filter.value }"
                @click="selectedHoldingFilter = filter.value"
              >
                {{ filter.label }}
              </el-button>
            </div>
          </div>
          
          <!-- 持仓卡片 -->
          <div class="holdings-cards">
            <!-- 空数据提示 -->
            <div v-if="!dashboardData?.holdings || dashboardData.holdings.length === 0" class="empty-holdings">
              <el-empty description="暂无数据" />
            </div>
            <div
              v-for="(item, index) in dashboardData?.holdings || []"
              :key="item.figure_id"
              class="holding-card"
              :class="getStatusClass(item.status)"
              @long-press="handleLongPress(item)"
            >
              <div class="card-image" v-if="item.image">
                <img :src="item.image" :alt="item.figure_name" />
              </div>
              <div class="card-content">
              <div class="card-header">
                <div class="card-title">{{ item.figure_name }}</div>
                <el-dropdown>
                  <span class="el-dropdown-link">
                    操作 ▼
                  </span>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item @click="sellAsset(item)">卖出</el-dropdown-item>
                      <el-dropdown-item @click="addPosition(item)">补仓</el-dropdown-item>
                      <el-dropdown-item v-if="item.status && item.status.includes('破位')" @click="cutLoss(item)">斩仓</el-dropdown-item>
                      <el-dropdown-item @click="editPrice(item)">修改现价</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
              <div class="card-body">
                <div class="card-info">
                  <div class="info-item">
                    <span class="label">库存:</span>
                    <span class="value">{{ item.stock || 1 }}体</span>
                  </div>
                  <div class="info-item">
                    <span class="label">状态:</span>
                    <span class="value">{{ item.status || '收藏中' }}</span>
                  </div>
                </div>
                <div class="card-divider"></div>
                <div class="card-prices">
                  <div class="price-item">
                    <span class="label">成本:</span>
                    <span class="value">¥{{ formatNumber(item.cost_price) }}</span>
                  </div>
                  <div class="price-item">
                    <span class="label">现价:</span>
                    <span class="value">¥{{ formatNumber(item.current_price) }}</span>
                  </div>
                  <div class="price-item">
                    <span class="label">盈亏:</span>
                    <span class="value" :class="{ positive: item.profit >= 0, negative: item.profit < 0 }">
                      {{ item.profit >= 0 ? '+' : '' }}¥{{ formatNumber(Math.abs(item.profit)) }} ({{ item.profit_percentage >= 0 ? '+' : '' }}{{ item.profit_percentage.toFixed(0) }}%)
                    </span>
                  </div>
                </div>
                <div class="card-footer">
                  <div class="footer-item" v-if="item.purchase_date">
                    <span class="label">入手:</span>
                    <span class="value">{{ item.purchase_date }}</span>
                  </div>
                  <div class="footer-item" v-if="item.holding_days">
                    <span class="label">持有:</span>
                    <span class="value">{{ item.holding_days }}天</span>
                  </div>
                  <div class="footer-item" v-if="item.market_share">
                    <span class="label">市值占比:</span>
                    <span class="value">{{ item.market_share }}%</span>
                  </div>
                </div>
              </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 行情视图 -->
      <div v-else-if="activeView === 'market'">
        <div class="market-section">
          <!-- 塑料小人指数 -->
          <div class="market-index">
            <div class="index-header">
              <h3>塑料小人指数 (HPI)</h3>
              <div class="index-stats">
                <div class="stat-item">
                  <div class="stat-label">涨:</div>
                  <div class="stat-value">{{ marketData?.index?.up_count || 0 }}</div>
                </div>
                <div class="stat-item">
                  <div class="stat-label">平:</div>
                  <div class="stat-value">{{ marketData?.index?.flat_count || 0 }}</div>
                </div>
                <div class="stat-item">
                  <div class="stat-label">跌:</div>
                  <div class="stat-value">{{ marketData?.index?.down_count || 0 }}</div>
                </div>
              </div>
            </div>
            <div class="index-content">
              <div class="index-main">
                <div class="index-value">{{ marketData?.index?.value || 0 }}</div>
                <div class="index-change" :class="{ positive: marketData?.index?.change >= 0, negative: marketData?.index?.change < 0 }">
                  {{ marketData?.index?.change >= 0 ? '↑' : '↓' }} {{ marketData?.index?.change >= 0 ? '+' : '' }}{{ marketData?.index?.change || 0 }} ({{ marketData?.index?.change_percentage >= 0 ? '+' : '' }}{{ marketData?.index?.change_percentage || 0 }}%)
                </div>
                <div class="index-volume">成交量: ¥{{ formatNumber(marketData?.index?.volume || 0) }}</div>
              </div>
              <div class="index-limits">
                <div class="limit-item">
                  <span class="limit-label">涨停(10%):</span>
                  <span class="limit-stocks">{{ marketData?.index?.limit_up || '无' }}</span>
                </div>
                <div class="limit-item">
                  <span class="limit-label">跌停(-10%):</span>
                  <span class="limit-stocks">{{ marketData?.index?.limit_down || '无' }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- K线图 -->
          <div class="kline-section">
            <div class="kline-header">
              <div class="kline-tabs">
                <el-button 
                  v-for="tab in klineTabs" 
                  :key="tab.value"
                  :class="{ active: selectedKlineTab === tab.value }"
                  @click="selectedKlineTab = tab.value"
                >
                  {{ tab.label }}
                </el-button>
              </div>
            </div>
            <div class="kline-chart-container">
              <div ref="marketKlineChart" class="kline-chart"></div>
              <div class="kline-indicators">
                <div class="indicator-item">
                  <span class="indicator-label">MACD:</span>
                  <span class="indicator-value">{{ marketData?.kline?.macd || '金叉' }}</span>
                </div>
                <div class="indicator-item">
                  <span class="indicator-label">RSI:</span>
                  <span class="indicator-value" :class="{ warning: marketData?.kline?.rsi > 60 }">
                    {{ marketData?.kline?.rsi || 68 }}({{ marketData?.kline?.rsi > 70 ? '超买区' : marketData?.kline?.rsi < 30 ? '超卖区' : '正常区' }})
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- 板块涨幅排行 -->
          <div class="sector-ranking">
            <div class="section-title">
              板块涨幅排行
            </div>
            <div class="sector-list">
              <div 
                v-for="(sector, index) in marketData?.sectors || []" 
                :key="sector.name"
                class="sector-item"
              >
                <div class="sector-rank">{{ index + 1 }}.</div>
                <div class="sector-info">
                  <div class="sector-name">{{ sector.name }}</div>
                  <div class="sector-stocks">{{ sector.stocks }}</div>
                </div>
                <div class="sector-change" :class="{ positive: sector.change >= 0, negative: sector.change < 0 }">
                  {{ sector.change >= 0 ? '+' : '' }}{{ sector.change }}%
                </div>
              </div>
            </div>
          </div>

          <!-- 我的自选股 -->
          <div class="watchlist-section">
            <div class="section-header">
              <div class="section-title">
                📈 我的自选股 (关注列表)
              </div>
              <el-button @click="addToWatchlist">[+添加]</el-button>
            </div>
            <div class="watchlist-table">
              <table>
                <thead>
                  <tr>
                    <th>名称</th>
                    <th>现价</th>
                    <th>涨跌</th>
                    <th>目标价</th>
                    <th>距离目标</th>
                  </tr>
                </thead>
                <tbody>
                  <tr 
                    v-for="stock in marketData?.watchlist || []" 
                    :key="stock.name"
                    class="watchlist-row"
                  >
                    <td>{{ stock.name }}</td>
                    <td>¥{{ formatNumber(stock.current_price) }}</td>
                    <td :class="{ positive: stock.change >= 0, negative: stock.change < 0 }">
                      {{ stock.change >= 0 ? '+' : '' }}{{ stock.change }}%
                    </td>
                    <td>¥{{ formatNumber(stock.target_price) }}</td>
                    <td>{{ stock.target_distance }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- 智能投研 -->
          <div class="research-section">
            <div class="section-title">
              💡 智能投研
            </div>
            <div class="research-card">
              <div class="research-item">
                <span class="research-label">机构评级:</span>
                <span class="research-value">{{ marketData?.research?.rating || 'GSC 初音韶华 买入' }}</span>
              </div>
              <div class="research-item">
                <span class="research-label">目标价:</span>
                <span class="research-value">{{ marketData?.research?.target_price || '¥2,800 (+40%)' }}</span>
              </div>
              <div class="research-item">
                <span class="research-label">止损价:</span>
                <span class="research-value">{{ marketData?.research?.stop_loss || '¥1,600 (-20%)' }}</span>
              </div>
              <div class="research-item">
                <span class="research-label">机构:</span>
                <span class="research-value">{{ marketData?.research?.institution || 'Hpoi研究院' }}</span>
              </div>
              <div class="research-item">
                <span class="research-label">日期:</span>
                <span class="research-value">{{ marketData?.research?.date || '2026-04-01' }}</span>
              </div>
              <div class="research-item">
                <span class="research-label">理由:</span>
                <span class="research-value">{{ marketData?.research?.reason || '再版停产公告+海景房属性+即将出荷' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 交易视图 -->
      <div v-else-if="activeView === 'trade'">
        <div class="trade-section">
          <div class="trade-header">
            <div class="trade-title">
            </div>
          </div>

          <!-- 本月交易统计 -->
          <div class="trade-stats">
            <h4>本月交易统计</h4>
            <div class="stats-grid">
              <div class="stat-item">
                <div class="stat-label">买入</div>
                <div class="stat-value">{{ tradeData?.monthly_stats?.buy_count || 0 }}笔</div>
                <div class="stat-amount">¥{{ formatNumber(tradeData?.monthly_stats?.buy_amount || 0) }}</div>
              </div>
              <div class="stat-item">
                <div class="stat-label">卖出</div>
                <div class="stat-value">{{ tradeData?.monthly_stats?.sell_count || 0 }}笔</div>
                <div class="stat-amount">¥{{ formatNumber(tradeData?.monthly_stats?.sell_amount || 0) }}</div>
              </div>
              <div class="stat-item">
                <div class="stat-label">净现金流</div>
                <div class="stat-value" :class="{ positive: tradeData?.monthly_stats?.net_cashflow >= 0, negative: tradeData?.monthly_stats?.net_cashflow < 0 }">
                  {{ tradeData?.monthly_stats?.net_cashflow >= 0 ? '+' : '' }}¥{{ formatNumber(Math.abs(tradeData?.monthly_stats?.net_cashflow || 0)) }}
                </div>
                <div class="stat-status" :class="{ positive: tradeData?.monthly_stats?.net_cashflow >= 0, negative: tradeData?.monthly_stats?.net_cashflow < 0 }">
                  {{ tradeData?.monthly_stats?.net_cashflow >= 0 ? '(收入>支出)' : '(支出>收入)' }}
                </div>
              </div>
            </div>
          </div>

          <!-- 快速操作 -->
          <div class="quick-actions">
            <h4>快速操作</h4>
            <div class="actions-grid">
              <el-button type="primary" @click="openBuyDialog">
                <el-icon><Plus /></el-icon> 买入
                <div class="action-desc">新增预定</div>
              </el-button>
              <el-button type="success" @click="openSellDialog">
                <el-icon><Minus /></el-icon> 卖出
                <div class="action-desc">标记转卖</div>
              </el-button>
              <el-button type="info" @click="openPaymentDialog">
                <el-icon><Money /></el-icon> 补款
                <div class="action-desc">支付尾款</div>
              </el-button>
              <el-button type="danger" @click="openCancelDialog">
                <el-icon><Close /></el-icon> 撤单
                <div class="action-desc">取消订单</div>
              </el-button>
            </div>
          </div>

          <!-- 交易流水 -->
          <div class="trade-flow">
            <div class="flow-header">
              <h4>交易流水 (按时间倒序)</h4>
              <el-button @click="showFilter = !showFilter">
                筛选 <el-icon><ArrowDown /></el-icon>
              </el-button>
            </div>

            <!-- 筛选条件 -->
            <div v-if="showFilter" class="filter-section">
              <div class="filter-row">
                <el-button 
                  v-for="type in tradeTypes" 
                  :key="type.value"
                  :class="{ active: selectedTradeType === type.value }"
                  @click="selectedTradeType = type.value"
                >
                  {{ type.label }}
                </el-button>
              </div>
              <div class="filter-row">
                <el-button 
                  v-for="year in tradeYears" 
                  :key="year.value"
                  :class="{ active: selectedTradeYear === year.value }"
                  @click="selectedTradeYear = year.value"
                >
                  {{ year.label }}
                </el-button>
                <el-button 
                  v-for="month in tradeMonths" 
                  :key="month.value"
                  :class="{ active: selectedTradeMonth === month.value }"
                  @click="selectedTradeMonth = month.value"
                >
                  {{ month.label }}
                </el-button>
              </div>
            </div>

            <!-- 交易记录 -->
            <div class="trade-records">
              <div 
                v-for="record in tradeData?.transactions || []" 
                :key="record.id"
                class="trade-record"
              >
                <div class="record-header">
                  <span class="record-date">📅 {{ record.date }}</span>
                  <span class="record-amount" :class="{ positive: record.amount >= 0, negative: record.amount < 0 }">
                    {{ record.amount >= 0 ? '+' : '' }}¥{{ formatNumber(Math.abs(record.amount)) }}
                  </span>
                </div>
                <div class="record-divider"></div>
                <div class="record-content">
                  <div class="record-title">{{ record.title }}</div>
                  <div class="record-details">
                    <span v-if="record.order_id" class="detail-item">订单号: {{ record.order_id }}</span>
                    <span v-if="record.buyer" class="detail-item">买家: {{ record.buyer }}</span>
                    <span v-if="record.platform" class="detail-item">平台: {{ record.platform }}</span>
                  </div>
                  <div class="record-status">
                    <span class="status-item">状态: {{ record.status }}</span>
                    <span v-if="record.payment_method" class="status-item">支付方式: {{ record.payment_method }}</span>
                    <span v-if="record.merchant" class="status-item">商户: {{ record.merchant }}</span>
                    <span v-if="record.fee" class="status-item">手续费: -¥{{ formatNumber(record.fee) }}</span>
                    <span v-if="record.net_profit" class="status-item" :class="{ positive: record.net_profit >= 0, negative: record.net_profit < 0 }">
                      净利润: {{ record.net_profit >= 0 ? '+' : '' }}¥{{ formatNumber(Math.abs(record.net_profit)) }}
                    </span>
                  </div>
                  <div class="record-actions">
                    <el-button v-if="record.actions" v-for="action in record.actions" :key="action" size="small" @click="handleTradeAction(action, record)">
                      {{ action }}
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 盈亏分析报表 -->
          <div class="profit-analysis">
            <h4>📊 盈亏分析报表</h4>
            <div class="analysis-grid">
              <div class="analysis-item">
                <div class="analysis-label">本年已实现收益</div>
                <div class="analysis-value" :class="{ positive: tradeData?.profit_analysis?.yearly_profit >= 0, negative: tradeData?.profit_analysis?.yearly_profit < 0 }">
                  {{ tradeData?.profit_analysis?.yearly_profit >= 0 ? '+' : '' }}¥{{ formatNumber(Math.abs(tradeData?.profit_analysis?.yearly_profit || 0)) }}
                </div>
              </div>
              <div class="analysis-item">
                <div class="analysis-label">本年交易胜率</div>
                <div class="analysis-value">
                  {{ tradeData?.profit_analysis?.win_rate || 0 }}% ({{ tradeData?.profit_analysis?.win_count || 0 }}胜{{ tradeData?.profit_analysis?.loss_count || 0 }}负)
                </div>
              </div>
              <div class="analysis-item">
                <div class="analysis-label">平均盈利</div>
                <div class="analysis-value positive">+¥{{ formatNumber(tradeData?.profit_analysis?.avg_profit || 0) }}/笔</div>
              </div>
              <div class="analysis-item">
                <div class="analysis-label">平均亏损</div>
                <div class="analysis-value negative">-¥{{ formatNumber(tradeData?.profit_analysis?.avg_loss || 0) }}/笔</div>
              </div>
              <div class="analysis-item full-width">
                <div class="analysis-label">最大单笔盈利</div>
                <div class="analysis-value positive">{{ tradeData?.profit_analysis?.max_profit_item || '' }} +¥{{ formatNumber(tradeData?.profit_analysis?.max_profit || 0) }}</div>
              </div>
              <div class="analysis-item full-width">
                <div class="analysis-label">最大单笔亏损</div>
                <div class="analysis-value negative">{{ tradeData?.profit_analysis?.max_loss_item || '' }} -¥{{ formatNumber(tradeData?.profit_analysis?.max_loss || 0) }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 收藏家模式内容 -->
    <div v-else class="collector-mode">
      <!-- 头部 -->
      <div class="collector-header">
        <div class="avatar">[头像]</div>
        <h3>我的塑料资产</h3>
        <div class="header-actions">
          <el-button @click="sharePoster">分享海报</el-button>
          <el-button @click="privacySettings">
            隐私设置 <el-icon><View /></el-icon>
          </el-button>
        </div>
      </div>

      <!-- 资产概览 -->
      <div class="collector-overview">
        <div class="overview-card">
          <div class="card-icon">💸</div>
          <div class="card-label">总投入</div>
          <div class="card-value">¥{{ formatNumber(collectorData?.summary?.total_investment || 0) }}</div>
        </div>
        <div class="overview-card">
          <div class="card-icon">💎</div>
          <div class="card-label">现估值</div>
          <div class="card-value">¥{{ formatNumber(collectorData?.summary?.total_valuation || 0) }}</div>
        </div>
        <div class="overview-card">
          <div class="card-icon">💰</div>
          <div class="card-label">回血额</div>
          <div class="card-value">¥{{ formatNumber(collectorData?.summary?.blood_money || 0) }}</div>
        </div>
      </div>

      <!-- 高价值藏品 -->
      <div class="valuable-collections">
        <div class="section-title">
          <el-icon><Picture /></el-icon> 高价值藏品
        </div>
        <div class="collections-grid">
          <div 
            v-for="item in collectorData?.valuable_items || []" 
            :key="item.id"
            class="collection-item"
            :class="{ 'sold-item': item.status === '已转卖' }"
          >
            <div class="item-image">
              <img :src="item.image" :alt="item.name" />
            </div>
            <div v-if="item.status === '已转卖'" class="item-status sold">
              已转卖
            </div>
            <div v-else class="item-profit" :class="{ positive: item.profit >= 0, negative: item.profit < 0 }">
              {{ item.profit >= 0 ? '💹+' : '🔻' }}¥{{ Math.abs(item.profit) }}
            </div>
            <div class="item-status">
              {{ item.status }}
            </div>
            <div v-if="item.sold_profit" class="sold-profit">
              利润¥{{ item.sold_profit }}
            </div>
          </div>
          <!-- 更多按钮 -->
          <div class="collection-item more-item">
            <div class="more-content">
              <span>+15</span>
              <p>更多</p>
            </div>
          </div>
          <div class="collection-item more-item">
            <div class="more-content">
              <span>+15</span>
              <p>更多</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 标签云 -->
      <div class="tag-cloud">
        <div class="section-title">
          <el-icon><CollectionTag /></el-icon> 标签云
        </div>
        <div class="tags">
          <span 
            v-for="tag in collectorData?.tags || []" 
            :key="tag.name"
            class="tag"
            @click="filterByTag(tag.name)"
          >
            #{{ tag.name }}({{ tag.count }})
          </span>
        </div>
      </div>

      <!-- 动态流 -->
      <div class="activity-feed">
        <div class="section-title">
          <el-icon><ChatDotRound /></el-icon> 动态流
        </div>
        <div class="activities">
          <div 
            v-for="(activity, index) in collectorData?.activities || []" 
            :key="index"
            class="activity-item"
          >
            <div class="activity-date">
              📅 {{ activity.date }}
            </div>
            <div class="activity-content">
              {{ activity.content }}
            </div>
            <div class="activity-actions">
              <el-button 
                v-for="action in activity.actions" 
                :key="action"
                size="small"
                @click="handleActivityAction(action, activity)"
              >
                {{ action }}
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 预警设置对话框 -->
    <el-dialog
      v-model="alertDialogVisible"
      title="设置预警"
      width="500px"
    >
      <el-form :model="alertForm" label-width="80px">
        <el-form-item label="手办">
          <el-select v-model="alertForm.figure_id" placeholder="选择手办">
            <el-option 
              v-for="figure in figures" 
              :key="figure.id" 
              :label="figure.name" 
              :value="figure.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="预警类型">
          <el-select v-model="alertForm.alert_type" placeholder="选择预警类型">
            <el-option value="price_drop" label="价格下跌" />
            <el-option value="price_rise" label="价格上涨" />
          </el-select>
        </el-form-item>
        <el-form-item label="阈值">
          <el-input v-model.number="alertForm.threshold" placeholder="输入预警阈值(%)" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="alertDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="createAlert">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 年度手办消费上限设置对话框 -->
    <el-dialog
      v-model="annualLimitDialogVisible"
      title="年度手办消费上限设置"
      width="500px"
    >
      <el-form :model="annualLimitForm" label-width="120px">
        <el-form-item label="年度消费上限">
          <el-input-number 
            v-model="annualLimitForm.limit" 
            :min="0" 
            :precision="2"
            :step="1000"
            style="width: 200px"
          />
          <span style="margin-left: 10px; color: #909399;">元</span>
        </el-form-item>
        <el-form-item>
          <div style="color: #909399; font-size: 12px; line-height: 1.5;">
            <p>提示：</p>
            <p>1. 设置年度手办消费上限后，系统将在您接近或超出上限时提醒您</p>
            <p>2. 设置为0表示不限制年度消费</p>
            <p>3. 该设置仅作为参考，不会阻止您继续购买手办</p>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="annualLimitDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveAnnualLimit" :loading="annualLimitLoading">
            保存设置
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store'
import axios from '../axios'
import * as echarts from 'echarts'
import { Refresh, Bell, TrendCharts, Top, Warning, List, ArrowUp, ArrowDown, Minus, View, Picture, CollectionTag, ChatDotRound, ArrowLeft, Download, Plus, Money, Close } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'Dashboard',
  components: {
    Refresh,
    Bell,
    TrendCharts,
    Top,
    Warning,
    List,
    ArrowUp,
    ArrowDown,
    Minus,
    View,
    Picture,
    CollectionTag,
    ChatDotRound,
    ArrowLeft,
    Download,
    Plus,
    Money,
    Close
  },
  setup() {
    const router = useRouter()
    const userStore = useUserStore()
    const klineChart = ref(null)
    const chartInstance = ref(null)
    const dashboardData = ref(null)
    const collectorData = ref(null)
    const loading = ref(true)
    const activeView = ref('asset')
    const selectedTimeRange = ref('1m')
    const showHoldings = ref(true)
    const alertDialogVisible = ref(false)
    const figures = ref([])
    const currentMode = ref('reseller') // reseller: 倒狗模式, collector: 收藏家模式
    const tradeData = ref(null)
    const marketData = ref(null)
    const showFilter = ref(false)
    const selectedTradeType = ref('all')
    const selectedTradeYear = ref('2026')
    const selectedTradeMonth = ref('')
    const marketKlineChart = ref(null)
    const marketChartInstance = ref(null)
    const selectedKlineTab = ref('day')
    const pieChart = ref(null)
    const pieChartInstance = ref(null)
    const pieChartInitialized = ref(false)
    const profitChart = ref(null)
    const profitChartInstance = ref(null)
    const selectedHoldingFilter = ref('all')
    
    // 年度消费上限设置
    const annualLimitDialogVisible = ref(false)
    const annualLimitForm = ref({
      limit: 0
    })
    const annualLimitLoading = ref(false)
    
    // 状态对照表
    const statusTable = ref(`
<table style="border-collapse: collapse; width: 100%; font-size: 12px;">
  <tr style="background-color: #f5f7fa; font-weight: bold;">
    <th style="border: 1px solid #dcdfe6; padding: 4px 8px; text-align: left;">状态标签</th>
    <th style="border: 1px solid #dcdfe6; padding: 4px 8px; text-align: left;">触发条件</th>
    <th style="border: 1px solid #dcdfe6; padding: 4px 8px; text-align: left;">颜色</th>
    <th style="border: 1px solid #dcdfe6; padding: 4px 8px; text-align: left;">操作建议</th>
  </tr>
  <tr>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px;">🚀 暴涨</td>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px;">单月涨幅 ≥ +15%</td>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px; color: green;">绿色</td>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px;">考虑止盈或分批减仓</td>
  </tr>
  <tr>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px;">📈 上涨</td>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px;">涨幅 +5% ~ +15%</td>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px; color: #67c23a;">浅绿</td>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px;">持有，设置+20%止盈点</td>
  </tr>
  <tr>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px;">➖ 横盘</td>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px;">波动 -5% ~ +5%</td>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px; color: #909399;">灰色</td>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px;">观望，适合建仓或定投</td>
  </tr>
  <tr>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px;">📉 告警</td>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px;">跌幅 -10% ~ -20%</td>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px; color: #e6a23c;">黄色</td>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px;">警惕，准备止损预案</td>
  </tr>
  <tr>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px;">🔴 破位</td>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px;">跌幅 ≥ -20% 或 破发</td>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px; color: #f56c6c;">红色</td>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px; font-weight: bold;">强制止损，避免深套</td>
  </tr>
  <tr>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px;">💀 退市</td>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px;">跌幅 ≥ -50% 或 绝版无市</td>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px; color: #000000;">黑色</td>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px;">流动性归零，账面资产作废</td>
  </tr>
</table>
    `)
    
    const klineTabs = [
      { label: '分时', value: 'minute' },
      { label: '日K', value: 'day' },
      { label: '周K', value: 'week' },
      { label: '月K', value: 'month' }
    ]
    
    const alertForm = ref({
      figure_id: '',
      alert_type: 'price_drop',
      threshold: 10
    })
    
    const viewTabs = [
      { label: '资产', value: 'asset' },
      { label: '行情', value: 'market' },
      { label: '交易', value: 'trade' }
    ]
    
    const timeRanges = [
      { label: '1月', value: '1m' },
      { label: '3月', value: '3m' },
      { label: '1年', value: '1y' },
      { label: '全', value: 'all' }
    ]
    
    const tradeTypes = [
      { label: '全部类型', value: 'all' },
      { label: '买入', value: 'buy' },
      { label: '卖出', value: 'sell' },
      { label: '补款', value: 'payment' },
      { label: '运费', value: 'shipping' },
      { label: '退款', value: 'refund' }
    ]
    
    const tradeYears = [
      { label: '2026年', value: '2026' },
      { label: '2025年', value: '2025' }
    ]
    
    const tradeMonths = [
      { label: '3月', value: '3' },
      { label: '2月', value: '2' },
      { label: '1月', value: '1' }
    ]
    
    const holdingFilters = [
      { label: '全部', value: 'all' },
      { label: '收藏中', value: 'collecting' },
      { label: '补款中', value: 'payment' },
      { label: '已转卖', value: 'sold' },
      { label: '破发 🔴', value: 'break-even' }
    ]
    
    // 格式化数字
    const formatNumber = (num) => {
      return num.toLocaleString()
    }
    
    // 退出登录
    const logout = () => {
      userStore.logout()
      router.push('/login')
    }
    
    // 初始化K线图
    const initKlineChart = () => {
      if (!klineChart.value) return
      
      if (chartInstance.value) {
        chartInstance.value.dispose()
      }
      
      chartInstance.value = echarts.init(klineChart.value)
      
      // 生成模拟数据
      const data = []
      for (let i = 0; i < 30; i++) {
        data.push([
          new Date(Date.now() - (30 - i) * 86400000).toISOString().substring(0, 10),
          2500 + i * 10 + (i % 5)
        ])
      }
      
      const xAxisData = data.map(item => item[0])
      const seriesData = data.map(item => item[1])
      
      const option = {
        tooltip: {
          trigger: 'axis',
          formatter: function(params) {
            return `${params[0].name}<br/>资产价值: ¥${params[0].value}`
          }
        },
        xAxis: {
          type: 'category',
          data: xAxisData,
          boundaryGap: false
        },
        yAxis: {
          type: 'value',
          axisLabel: {
            formatter: '¥{value}'
          }
        },
        series: [
          {
            data: seriesData,
            type: 'line',
            smooth: true,
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                {
                  offset: 0,
                  color: 'rgba(33, 150, 243, 0.5)'
                },
                {
                  offset: 1,
                  color: 'rgba(33, 150, 243, 0.1)'
                }
              ])
            },
            lineStyle: {
              color: '#2196F3',
              width: 2
            },
            symbol: 'circle',
            symbolSize: 4
          }
        ]
      }
      
      chartInstance.value.setOption(option)
      
      // 响应式调整
      const handleResize = () => {
        chartInstance.value?.resize()
      }
      
      window.addEventListener('resize', handleResize)
      
      // 清理函数
      onUnmounted(() => {
        window.removeEventListener('resize', handleResize)
        chartInstance.value?.dispose()
      })
    }

    // 初始化资产分布饼图（风险状态分布 - 健康度仪表盘）
    const initPieChart = () => {
      if (!pieChart.value) {
        return
      }
      
      if (pieChartInstance.value) {
        pieChartInstance.value.dispose()
      }
      
      pieChartInstance.value = echarts.init(pieChart.value)
      
      // 使用后端返回的风险状态分布数据
      const riskData = dashboardData.value?.risk_distribution || []
      
      // 如果没有数据，显示空状态
      if (riskData.length === 0) {
        const option = {
          title: {
            text: '暂无数据',
            left: 'center',
            top: 'center',
            textStyle: {
              color: '#909399',
              fontSize: 14
            }
          }
        }
        pieChartInstance.value.setOption(option)
        return
      }
      
      // 提取图例数据
      const legendData = riskData.map(item => item.name)
      
      const option = {
        tooltip: {
          trigger: 'item',
          formatter: function(params) {
            const data = params.data
            return `${data.name}<br/>市值: ¥${formatNumber(data.value)}<br/>数量: ${data.count}个<br/>占比: ${params.percent}%`
          }
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          data: legendData,
          textStyle: {
            fontSize: 12
          }
        },
        series: [
          {
            name: '健康度分布',
            type: 'pie',
            radius: ['40%', '70%'],  // 环形图
            center: ['60%', '50%'],
            data: riskData,
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            },
            label: {
              show: true,
              formatter: '{b}\n{d}%'
            },
            labelLine: {
              show: true
            }
          }
        ]
      }
      
      pieChartInstance.value.setOption(option)
      
      // 响应式调整
      const handleResize = () => {
        pieChartInstance.value?.resize()
      }
      
      window.addEventListener('resize', handleResize)
      
      // 清理函数
      onUnmounted(() => {
        window.removeEventListener('resize', handleResize)
        pieChartInstance.value?.dispose()
      })
    }

    // 初始化收益曲线
    const initProfitChart = () => {
      if (!profitChart.value) return
      
      if (profitChartInstance.value) {
        profitChartInstance.value.dispose()
      }
      
      profitChartInstance.value = echarts.init(profitChart.value)
      
      // 生成模拟数据
      const data = []
      for (let i = 0; i < 30; i++) {
        data.push([
          new Date(Date.now() - (30 - i) * 86400000).toISOString().substring(0, 10),
          100 + i * 0.5 + (i % 5)
        ])
      }
      
      const xAxisData = data.map(item => item[0])
      const seriesData = data.map(item => item[1])
      
      const option = {
        tooltip: {
          trigger: 'axis',
          formatter: function(params) {
            return `${params[0].name}<br/>收益率: ${params[0].value}%`
          }
        },
        xAxis: {
          type: 'category',
          data: xAxisData,
          boundaryGap: false
        },
        yAxis: {
          type: 'value',
          axisLabel: {
            formatter: '{value}%'
          }
        },
        series: [
          {
            data: seriesData,
            type: 'line',
            smooth: true,
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                {
                  offset: 0,
                  color: 'rgba(76, 175, 80, 0.5)'
                },
                {
                  offset: 1,
                  color: 'rgba(76, 175, 80, 0.1)'
                }
              ])
            },
            lineStyle: {
              color: '#4CAF50',
              width: 2
            },
            symbol: 'circle',
            symbolSize: 4
          }
        ]
      }
      
      profitChartInstance.value.setOption(option)
      
      // 响应式调整
      const handleResize = () => {
        profitChartInstance.value?.resize()
      }
      
      window.addEventListener('resize', handleResize)
      
      // 清理函数
      onUnmounted(() => {
        window.removeEventListener('resize', handleResize)
        profitChartInstance.value?.dispose()
      })
    }
    
    // 获取手办列表
    const fetchFigures = async () => {
      try {
        const res = await axios.get('/figures/')
        figures.value = res
      } catch (error) {
        console.error('获取手办列表失败:', error)
      }
    }
    
    // 获取看板数据
    const fetchDashboardData = async () => {
      loading.value = true
      try {
        const res = await axios.get(`/assets/dashboard?time_range=${selectedTimeRange.value}`)
        // axios拦截器已返回response.data，所以res就是数据
        dashboardData.value = res
        // 使用更长的延迟确保DOM元素完全渲染
        setTimeout(() => {
          if (pieChart.value) {
            initKlineChart()
            initPieChart()
            initProfitChart()
          } else {
            // 再试一次
            setTimeout(() => {
              initKlineChart()
              initPieChart()
              initProfitChart()
            }, 200)
          }
        }, 100)
      } catch (error) {
        console.error('获取看板数据失败:', error)
        // 不生成模拟数据，保持空状态
        dashboardData.value = {
          summary: {
            total_assets: 0,
            daily_change: 0,
            daily_change_percentage: 0,
            plastic_index: 0,
            sh_index: 0,
            outperform_percentage: 0,
            position: '空仓',
            monthly_purchases: 0
          },
          profit: {
            floating: 0,
            realized: 0,
            total_rate: 0
          },
          holdings: [],
          risk_distribution: []
        }
        // 清空图表数据
        if (klineChartInstance.value) {
          klineChartInstance.value.dispose()
          klineChartInstance.value = null
        }
        if (pieChartInstance.value) {
          pieChartInstance.value.dispose()
          pieChartInstance.value = null
        }
        if (profitChartInstance.value) {
          profitChartInstance.value.dispose()
          profitChartInstance.value = null
        }
      } finally {
        loading.value = false
      }
    }
    
    // 刷新数据
    const refreshData = () => {
      fetchDashboardData()
    }

    // 刷新交易数据
    const refreshTradeData = () => {
      fetchTradeData()
    }

    // 打开预警设置
    const openAlertSettings = () => {
      fetchFigures()
      alertDialogVisible.value = true
    }
    
    // 创建预警
    const createAlert = async () => {
      try {
        await axios.post('/assets/alerts', alertForm.value)
        alertDialogVisible.value = false
        ElMessage.success('预警设置成功')
      } catch (error) {
        console.error('创建预警失败:', error)
        ElMessage.error('预警设置失败')
      }
    }
    
    // 显示年度消费上限设置对话框
    const showAnnualLimitDialog = async () => {
      await loadAnnualLimit()
      annualLimitDialogVisible.value = true
    }
    
    // 加载年度消费上限设置
    const loadAnnualLimit = async () => {
      try {
        const response = await axios.get('/assets/settings/annual-limit')
        // axios拦截器已返回response.data，所以response就是数据
        annualLimitForm.value.limit = response.annual_spending_limit || 0
      } catch (error) {
        console.error('加载年度消费上限失败:', error)
        ElMessage.error('加载设置失败')
      }
    }
    
    // 保存年度消费上限设置
    const saveAnnualLimit = async () => {
      annualLimitLoading.value = true
      try {
        await axios.post('/assets/settings/annual-limit', null, {
          params: {
            limit: annualLimitForm.value.limit
          }
        })
        annualLimitDialogVisible.value = false
        ElMessage.success('年度消费上限设置成功')
      } catch (error) {
        console.error('保存年度消费上限失败:', error)
        ElMessage.error(error.response?.data?.detail || '设置失败')
      } finally {
        annualLimitLoading.value = false
      }
    }
    
    // 切换持仓明细显示
    const toggleHoldings = () => {
      showHoldings.value = !showHoldings.value
    }
    
    // 卖出资产
    const sellAsset = (item) => {
      ElMessageBox.confirm(`确定要卖出 ${item.figure_name} 吗？`, '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          await axios.post('/assets/transactions', {
            figure_id: item.figure_id,
            transaction_type: 'sell',
            price: item.current_price,
            notes: '手动卖出'
          })
          ElMessage.success('卖出成功')
          fetchDashboardData()
        } catch (error) {
          console.error('卖出失败:', error)
          ElMessage.error('卖出失败')
        }
      })
    }
    
    // 补仓
    const addPosition = (item) => {
      ElMessage.info('补仓功能开发中')
    }
    
    // 获取状态对应的CSS类名
    const getStatusClass = (status) => {
      if (!status) return ''
      if (status.includes('暴涨')) return 'status-surge'
      if (status.includes('上涨')) return 'status-rise'
      if (status.includes('横盘')) return 'status-flat'
      if (status.includes('告警')) return 'status-warning'
      if (status.includes('退市')) return 'status-delisted'
      if (status.includes('破位')) return 'status-break'
      return ''
    }

    // 斩仓
    const cutLoss = (item) => {
      ElMessageBox.confirm(`确定要斩仓 ${item.figure_name} 吗？`, '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'danger'
      }).then(async () => {
        try {
          await axios.post('/assets/transactions', {
            figure_id: item.figure_id,
            transaction_type: 'sell',
            price: item.current_price,
            notes: '斩仓'
          })
          ElMessage.success('斩仓成功')
          fetchDashboardData()
        } catch (error) {
          console.error('斩仓失败:', error)
          ElMessage.error('斩仓失败')
        }
      })
    }
    
    // 处理长按卡片
    const handleLongPress = (item) => {
      ElMessageBox.confirm(`选择操作: ${item.figure_name}`, '长按操作', {
        confirmButtonText: '标记转卖',
        cancelButtonText: '修改现价',
        type: 'info'
      }).then(async () => {
        // 标记转卖
        await sellAsset(item)
      }).catch(() => {
        // 修改现价
        editPrice(item)
      })
    }
    
    // 编辑现价
    const editPrice = (item) => {
      ElMessageBox.prompt(`请输入 ${item.figure_name} 的新现价:`, '修改现价', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputPattern: /^\d+(\.\d{1,2})?$/,
        inputErrorMessage: '请输入有效的价格'
      }).then(async (result) => {
        try {
          await axios.post('/assets/price-history', {
            figure_id: item.figure_id,
            current_price: parseFloat(result.value),
            date: new Date().toISOString()
          })
          ElMessage.success('现价修改成功')
          fetchDashboardData()
        } catch (error) {
          console.error('修改现价失败:', error)
          ElMessage.error('修改现价失败')
        }
      })
    }
    
    // 获取收藏家模式数据
    const fetchCollectorData = async () => {
      loading.value = true
      try {
        const res = await axios.get('/assets/collector/dashboard')
        collectorData.value = res
      } catch (error) {
        console.error('获取收藏家模式数据失败:', error)
        // 生成模拟数据
        collectorData.value = {
          summary: {
            total_investment: 50000,
            total_valuation: 80000,
            blood_money: 12000
          },
          valuable_items: [
            {
              id: 1,
              name: "初音韶华",
              image: "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=anime%20figure%20Hatsune%20Miku%20with%20colorful%20hair%20and%20modern%20outfit&image_size=square",
              profit: 1200,
              status: "海景房"
            },
            {
              id: 2,
              name: "蕾姆婚纱",
              image: "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=anime%20figure%20Rem%20in%20wedding%20dress%20blue%20hair&image_size=square",
              profit: 800,
              status: "小赚"
            },
            {
              id: 3,
              name: "Saber",
              image: "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=anime%20figure%20Saber%20from%20Fate%20series%20in%20blue%20dress&image_size=square",
              profit: -200,
              status: "破发"
            },
            {
              id: 4,
              name: "艾米莉亚",
              image: "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=anime%20figure%20Emilia%20with%20silver%20hair%20and%20blue%20dress&image_size=square",
              status: "已转卖",
              sold_profit: 500
            }
          ],
          tags: [
            {"name": "海景房", "count": 3},
            {"name": "破发区", "count": 5},
            {"name": "待补款", "count": 2},
            {"name": "已出坑", "count": 8}
          ],
          activities: [
            {
              "date": "2026-03-15",
              "content": "入手初音韶华 180天，估值上涨150%",
              "actions": ["生成分享卡片", "查看详情"]
            },
            {
              "date": "2026-02-20",
              "content": "蕾姆婚纱补款完成，等待发货",
              "actions": ["查看详情"]
            }
          ]
        }
      } finally {
        loading.value = false
      }
    }
    
    // 切换模式
    const toggleMode = () => {
      currentMode.value = currentMode.value === 'reseller' ? 'collector' : 'reseller'
      if (currentMode.value === 'collector') {
        fetchCollectorData()
      }
    }
    
    // 分享海报
    const sharePoster = () => {
      ElMessage.info('分享海报功能开发中')
    }
    
    // 隐私设置
    const privacySettings = () => {
      ElMessage.info('隐私设置功能开发中')
    }
    
    // 按标签筛选
    const filterByTag = (tagName) => {
      ElMessage.info(`按标签 ${tagName} 筛选`)
    }
    
    // 处理动态流操作
    const handleActivityAction = (action, activity) => {
      ElMessage.info(`执行操作: ${action}`)
    }
    
    // 获取交易数据
    const fetchTradeData = async () => {
      try {
        const res = await axios.get('/assets/trade/dashboard')
        tradeData.value = res
      } catch (error) {
        console.error('获取交易数据失败:', error)
        // 生成模拟数据
        tradeData.value = {
          monthly_stats: {
            buy_count: 3,
            buy_amount: 5600,
            sell_count: 2,
            sell_amount: 2400,
            net_cashflow: -3200
          },
          transactions: [
            {
              id: 1,
              date: '04-02 14:30',
              amount: -800,
              title: '买入: 初音未来 韶华 Ver. (尾款支付)',
              order_id: 'ORD20260402001',
              status: '✅ 成功',
              payment_method: '支付宝',
              merchant: 'AmiAmi',
              actions: ['查看订单', '申请售后', '下载电子发票']
            },
            {
              id: 2,
              date: '03-28 10:15',
              amount: 1200,
              title: '卖出: 蕾姆 婚纱 Ver.',
              buyer: '闲鱼用户_xxx',
              platform: '闲鱼',
              status: '✅ 已到账',
              fee: 7.2,
              net_profit: 292.8,
              actions: ['查看买家信息', '物流信息', '评价']
            },
            {
              id: 3,
              date: '03-20 09:00',
              amount: -200,
              title: '定金: Saber 礼服 Ver. (预定锁定)',
              status: '⏳ 持有中',
              estimated_payment: '2026-06',
              actions: ['补款提醒设置', '转让定金', '放弃定金']
            }
          ],
          profit_analysis: {
            yearly_profit: 3400,
            win_rate: 66.7,
            win_count: 4,
            loss_count: 2,
            avg_profit: 850,
            avg_loss: 200,
            max_profit: 1200,
            max_profit_item: '初音韶华',
            max_loss: 200,
            max_loss_item: '蕾姆'
          }
        }
      }
    }
    
    // 导出账单
    const exportBill = () => {
      ElMessage.info('账单导出功能开发中')
    }
    
    // 打开买入对话框
    const openBuyDialog = () => {
      ElMessage.info('买入功能开发中')
    }
    
    // 打开卖出对话框
    const openSellDialog = () => {
      ElMessage.info('卖出功能开发中')
    }
    
    // 打开补款对话框
    const openPaymentDialog = () => {
      ElMessage.info('补款功能开发中')
    }
    
    // 打开撤单对话框
    const openCancelDialog = () => {
      ElMessage.info('撤单功能开发中')
    }
    
    // 处理交易操作
    const handleTradeAction = (action, record) => {
      ElMessage.info(`执行交易操作: ${action}`)
    }
    
    // 初始化行情K线图
    const initMarketKlineChart = () => {
      if (!marketKlineChart.value) return
      
      if (marketChartInstance.value) {
        marketChartInstance.value.dispose()
      }
      
      marketChartInstance.value = echarts.init(marketKlineChart.value)
      
      // 生成模拟数据
      const data = []
      for (let i = 0; i < 30; i++) {
        data.push([
          new Date(Date.now() - (30 - i) * 86400000).toISOString().substring(0, 10),
          2800 + i * 2 + (i % 5)
        ])
      }
      
      const xAxisData = data.map(item => item[0])
      const seriesData = data.map(item => item[1])
      
      const option = {
        tooltip: {
          trigger: 'axis',
          formatter: function(params) {
            return `${params[0].name}<br/>指数: ${params[0].value}`
          }
        },
        xAxis: {
          type: 'category',
          data: xAxisData,
          boundaryGap: false
        },
        yAxis: {
          type: 'value',
          axisLabel: {
            formatter: '{value}'
          }
        },
        series: [
          {
            data: seriesData,
            type: 'line',
            smooth: true,
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                {
                  offset: 0,
                  color: 'rgba(76, 175, 80, 0.5)'
                },
                {
                  offset: 1,
                  color: 'rgba(76, 175, 80, 0.1)'
                }
              ])
            },
            lineStyle: {
              color: '#4CAF50',
              width: 2
            },
            symbol: 'circle',
            symbolSize: 4
          }
        ]
      }
      
      marketChartInstance.value.setOption(option)
      
      // 响应式调整
      const handleResize = () => {
        marketChartInstance.value?.resize()
      }
      
      window.addEventListener('resize', handleResize)
      
      // 清理函数
      onUnmounted(() => {
        window.removeEventListener('resize', handleResize)
        marketChartInstance.value?.dispose()
      })
    }
    
    // 获取行情数据
      const fetchMarketData = async () => {
        try {
          const res = await axios.get('/assets/market/dashboard')
          // axios拦截器已返回response.data，所以res就是数据
          marketData.value = res
          initMarketKlineChart()
        } catch (error) {
          console.error('获取行情数据失败:', error)
          // 生成模拟数据
          marketData.value = {
            index: {
              value: 2847.35,
              change: 45.20,
              change_percentage: 1.61,
              volume: 230000000,
              up_count: 1230,
              flat_count: 45,
              down_count: 320,
              limit_up: '初音、蕾姆、狂三',
              limit_down: '无'
            },
            kline: {
              macd: '金叉',
              rsi: 68
            },
            sectors: [
              {
                name: '初音未来概念',
                change: 8.5,
                stocks: '初音韶华、赛车音、雪未来'
              },
              {
                name: 'FGO系列',
                change: 5.2,
                stocks: '摩根、妖兰、提亚马特'
              },
              {
                name: '碧蓝航线',
                change: 3.1,
                stocks: '信浓、柴郡、埃吉尔'
              },
              {
                name: '原神系列',
                change: -2.3,
                stocks: '雷神、神子(高位回调)'
              }
            ],
            watchlist: [
              {
                name: '初音韶华',
                current_price: 2000,
                change: 15,
                target_price: 2500,
                target_distance: '还差25%'
              },
              {
                name: '蕾姆婚纱',
                current_price: 1200,
                change: -5,
                target_price: 1500,
                target_distance: '还需上涨30%'
              },
              {
                name: '(观望中)',
                current_price: 800,
                change: 0,
                target_price: 600,
                target_distance: '等破发入手'
              }
            ],
            research: {
              rating: 'GSC 初音韶华 买入',
              target_price: '¥2,800 (+40%)',
              stop_loss: '¥1,600 (-20%)',
              institution: 'Hpoi研究院',
              date: '2026-04-01',
              reason: '再版停产公告+海景房属性+即将出荷'
            }
          }
          initMarketKlineChart()
        }
      }
    
    // 添加到自选股
    const addToWatchlist = () => {
      ElMessage.info('添加自选股功能开发中')
    }
    
    // 监听时间范围变化
    watch(selectedTimeRange, () => {
      fetchDashboardData()
    })
    
    // 监听活跃视图变化
    watch(activeView, async (newView) => {
      if (newView === 'asset') {
        await fetchDashboardData()
        // 确保DOM更新后再初始化图表
        await nextTick()
        initPieChart()
        initProfitChart()
      } else if (newView === 'trade') {
        fetchTradeData()
      } else if (newView === 'market') {
        fetchMarketData()
      }
    })
    
    // 组件挂载时
    onMounted(() => {
      fetchDashboardData()
      // 如果有token但用户信息为空，获取用户信息
      if (localStorage.getItem('token') && !userStore.currentUser) {
        userStore.fetchUser()
      }
    })
    
    return {
      dashboardData,
      collectorData,
      tradeData,
      marketData,
      loading,
      activeView,
      viewTabs,
      selectedTimeRange,
      timeRanges,
      showHoldings,
      alertDialogVisible,
      alertForm,
      figures,
      klineChart,
      marketKlineChart,
      pieChart,
      profitChart,
      userStore,
      currentMode,
      showFilter,
      selectedTradeType,
      selectedTradeYear,
      selectedTradeMonth,
      tradeTypes,
      tradeYears,
      tradeMonths,
      klineTabs,
      selectedKlineTab,
      statusTable,
      // 年度消费上限设置
      annualLimitDialogVisible,
      annualLimitForm,
      annualLimitLoading,
      showAnnualLimitDialog,
      saveAnnualLimit,
      formatNumber,
      refreshData,
      refreshTradeData,
      openAlertSettings,
      createAlert,
      toggleHoldings,
      sellAsset,
      addPosition,
      cutLoss,
      getStatusClass,
      toggleMode,
      sharePoster,
      privacySettings,
      filterByTag,
      handleActivityAction,
      fetchTradeData,
      fetchMarketData,
      exportBill,
      openBuyDialog,
      openSellDialog,
      openPaymentDialog,
      openCancelDialog,
      handleTradeAction,
      addToWatchlist,
      logout
    }
  }
}
</script>

<style scoped>
.orders-container {
  margin-top: 20px;
  width: 100%;
  max-width: 1650px;
  margin-left: 50px;
  margin-right: 50px;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #e0e0e0;
}

.header h2 {
  margin: 0;
  color: #333;
  font-size: 24px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

.view-tabs {
  display: flex;
  gap: 10px;
}

.view-tabs .el-button.active {
  background-color: #1976D2;
  color: white;
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 10px 15px;
  background-color: white;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.username {
  font-size: 14px;
  font-weight: 500;
  color: #555;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.btn-logout {
  background-color: #f44336;
  color: white;
  padding: 8px 16px;
  font-size: 14px;
}

.btn-logout:hover {
  background-color: #da190b;
}

/* 倒狗模式操作栏 */
.reseller-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.reseller-actions .view-tabs {
  display: flex;
  gap: 10px;
}

.reseller-actions .action-buttons {
  display: flex;
  gap: 10px;
}

/* 资产概览区 */
.asset-overview {
  display: flex;
  gap: 30px;
  margin-bottom: 20px;
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.overview-item {
  display: flex;
  flex-direction: column;
}

.overview-item .label {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.overview-item .value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.overview-item .value.positive {
  color: #4CAF50;
}

.overview-item .value.negative {
  color: #F44336;
}

/* 仓位状态颜色 */
.position-value.position-gray {
  color: #909399;
  font-weight: bold;
}

.position-value.position-blue {
  color: #409EFF;
  font-weight: bold;
}

.position-value.position-green {
  color: #67C23A;
  font-weight: bold;
}

.position-value.position-yellow {
  color: #E6A23C;
  font-weight: bold;
}

.position-value.position-red {
  color: #F56C6C;
  font-weight: bold;
}

.position-value.position-black {
  color: #303133;
  font-weight: bold;
  background-color: #F2F6FC;
  padding: 2px 8px;
  border-radius: 4px;
}

/* 分隔线 */
.divider {
  height: 2px;
  background-color: #e0e0e0;
  margin: 20px 0;
}

/* 指数对比 */
.index-comparison {
  display: flex;
  gap: 30px;
  margin-bottom: 20px;
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.index-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.index-item .label {
  font-size: 14px;
  color: #666;
}

.index-item .value {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.index-item .value.positive {
  color: #4CAF50;
}

/* 主内容区 */
.main-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

/* 左侧K线图 */
.left-section {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 15px;
  color: #333;
}

.time-range {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.time-range .el-button.active {
  background-color: #1976D2;
  color: white;
}

.kline-container {
  height: 300px;
  margin-bottom: 20px;
}

.kline-chart {
  width: 100%;
  height: 100%;
  background: linear-gradient(to bottom, #f0f9ff 0%, #ffffff 100%);
  border-radius: 4px;
  overflow: hidden;
}

.kline-info {
  display: flex;
  justify-content: space-between;
  padding-top: 10px;
  border-top: 1px solid #e0e0e0;
}

.kline-info .info-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.kline-info .label {
  font-size: 14px;
  color: #666;
}

.kline-info .value {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

/* 右侧涨跌排行 */
.right-section {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.rankings-list {
  margin-bottom: 30px;
}

.ranking-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.ranking-item .rank {
  font-weight: bold;
  width: 30px;
}

.ranking-item .name {
  flex: 1;
}

.ranking-item .change {
  font-weight: bold;
  width: 80px;
  text-align: right;
}

.ranking-item .change.positive {
  color: #4CAF50;
}

.ranking-item .change.negative {
  color: #F44336;
}

.ranking-item .trend {
  width: 30px;
  text-align: center;
}

.ranking-item .trend.up {
  color: #4CAF50;
}

.ranking-item .trend.down {
  color: #F44336;
}

.ranking-item .alert {
  background-color: #FF9800;
  color: white;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
}

/* 操作建议 */
.advice-section {
  margin-top: 30px;
}

.advice-content {
  background-color: #f5f5f5;
  padding: 15px;
  border-radius: 8px;
}

.advice-item {
  line-height: 1.5;
  color: #333;
}

/* 持仓明细 */
.holdings-section {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.holdings-table {
  overflow-x: auto;
}

.holdings-table table {
  width: 100%;
  border-collapse: collapse;
}

.holdings-table th,
.holdings-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}

.holdings-table th {
  background-color: #f5f5f5;
  font-weight: bold;
  color: #333;
}

.holding-row.break-even {
  background-color: #FFF3E0;
}

.holdings-table td.positive {
  color: #4CAF50;
  font-weight: bold;
}

.holdings-table td.negative {
  color: #F44336;
  font-weight: bold;
}

.actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.status-badge {
  margin-right: 10px;
  font-size: 12px;
  font-weight: bold;
}

.status-badge.break-even {
  color: #F44336;
}

/* 图表区域 */
.chart-section {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.chart-item {
  flex: 1;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.pie-chart,
.profit-chart {
  height: 300px;
  width: 100%;
}

/* 盈亏分析 */
.profit-analysis {
  margin-bottom: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.analysis-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-top: 15px;
}

.analysis-item {
  text-align: center;
}

.analysis-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.analysis-value {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 3px;
}

.analysis-desc {
  font-size: 12px;
  color: #999;
}

/* 筛选条件 */
.filter-section {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f5f5;
  border-radius: 6px;
}

.filter-row {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.search-input {
  width: 200px;
}

/* 持仓卡片 */
.holdings-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.holding-card {
  background-color: #f9f9f9;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 15px;
  transition: all 0.3s ease;
}

.holding-card:hover {
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.holding-card.break-even {
  border-left: 4px solid #ff4d4f;
  background-color: #fff2f0;
}

/* 持仓状态样式 */
.holding-card.status-surge {
  border-left: 4px solid #52c41a;
  background-color: #f6ffed;
}

.holding-card.status-rise {
  border-left: 4px solid #95de64;
  background-color: #f6ffed;
}

.holding-card.status-flat {
  border-left: 4px solid #8c8c8c;
  background-color: #f5f5f5;
}

.holding-card.status-warning {
  border-left: 4px solid #faad14;
  background-color: #fffbe6;
}

.holding-card.status-break {
  border-left: 4px solid #ff4d4f;
  background-color: #fff2f0;
}

.holding-card.status-delisted {
  border-left: 4px solid #000000;
  background-color: #f0f0f0;
}

/* 持仓列表空数据提示 */
.empty-holdings {
  width: 100%;
  padding: 40px 0;
  display: flex;
  justify-content: center;
  align-items: center;
  grid-column: 1 / -1; /* 让空数据提示占据整个网格宽度 */
  min-height: 200px; /* 确保有足够的高度 */
}

/* 持仓卡片图片样式 */
.holding-card {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
}

.holding-card .card-image {
  width: 80px;
  height: 80px;
  min-width: 80px;
  margin-right: 15px;
  border-radius: 8px;
  overflow: hidden;
  background-color: #f0f0f0;
}

.holding-card .card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.holding-card .card-content {
  flex: 1;
  min-width: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

/* 移除操作按钮的黑框 */
.card-header .el-dropdown-link {
  outline: none !important;
  border: none !important;
  box-shadow: none !important;
}

.card-header .el-dropdown-link:focus,
.card-header .el-dropdown-link:hover,
.card-header .el-dropdown-link:active {
  outline: none !important;
  border: none !important;
  box-shadow: none !important;
}

/* 状态帮助按钮样式 */
.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-help-button {
  width: 24px;
  height: 24px;
  min-width: 24px;
  padding: 0;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: bold;
}

.card-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.card-info {
  display: flex;
  gap: 20px;
}

.info-item {
  display: flex;
  gap: 5px;
}

.info-item .label {
  color: #666;
  font-size: 14px;
}

.info-item .value {
  font-weight: 500;
  font-size: 14px;
}

.card-divider {
  height: 1px;
  background-color: #e8e8e8;
  margin: 10px 0;
}

.card-prices {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.price-item {
  display: flex;
  gap: 10px;
  align-items: center;
}

.price-item .label {
  width: 50px;
  color: #666;
  font-size: 14px;
}

.price-item .value {
  font-weight: 500;
  font-size: 14px;
}

.price-item .emoji {
  margin-left: 5px;
  font-size: 16px;
}

.card-footer {
  display: flex;
  gap: 20px;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #e8e8e8;
}

.footer-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
}

.footer-item .label {
  color: #999;
}

.footer-item .value {
  color: #666;
  font-weight: 500;
}

/* 收藏家模式 */
.collector-mode {
  padding: 20px;
}

/* 收藏家头部 */
.collector-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 30px;
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.collector-header .avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.collector-header h3 {
  margin: 0;
  color: #333;
  font-size: 20px;
  font-weight: 600;
}

.collector-header .header-actions {
  display: flex;
  gap: 10px;
}

/* 资产概览 */
.collector-overview {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.overview-card {
  background-color: white;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
  transition: transform 0.3s ease;
}

.overview-card:hover {
  transform: translateY(-5px);
}

.overview-card .card-icon {
  font-size: 32px;
  margin-bottom: 10px;
}

.overview-card .card-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.overview-card .card-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

/* 高价值藏品 */
.valuable-collections {
  margin-bottom: 30px;
}

.valuable-collections .section-title {
  margin-bottom: 20px;
  color: #333;
  font-size: 18px;
  font-weight: 600;
}

.collections-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.collection-item {
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: relative;
  transition: transform 0.3s ease;
}

.collection-item:hover {
  transform: translateY(-5px);
}

.collection-item .item-image {
  width: 100%;
  height: 200px;
  overflow: hidden;
}

.collection-item .item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.collection-item:hover .item-image img {
  transform: scale(1.05);
}

.collection-item .item-profit {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
}

.collection-item .item-profit.positive {
  background-color: rgba(76, 175, 80, 0.8);
}

.collection-item .item-profit.negative {
  background-color: rgba(244, 67, 54, 0.8);
}

.collection-item .item-status {
  padding: 15px;
  text-align: center;
  font-weight: bold;
  color: #333;
}

.collection-item.sold-item .item-status.sold {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  background-color: rgba(255, 152, 0, 0.8);
  color: white;
  padding: 5px;
  font-size: 14px;
}

.collection-item.sold-item .sold-profit {
  padding: 0 15px 15px;
  text-align: center;
  color: #666;
  font-size: 14px;
}

.collection-item.more-item {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  border: 2px dashed #e0e0e0;
  min-height: 200px;
}

.collection-item.more-item .more-content {
  text-align: center;
}

.collection-item.more-item .more-content span {
  display: block;
  font-size: 32px;
  font-weight: bold;
  color: #999;
  margin-bottom: 10px;
}

.collection-item.more-item .more-content p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

/* 标签云 */
.tag-cloud {
  margin-bottom: 30px;
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.tag-cloud .section-title {
  margin-bottom: 20px;
  color: #333;
  font-size: 18px;
  font-weight: 600;
}

.tag-cloud .tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.tag-cloud .tag {
  background-color: #f0f0f0;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  color: #333;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tag-cloud .tag:hover {
  background-color: #1976D2;
  color: white;
  transform: scale(1.05);
}

/* 动态流 */
.activity-feed {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.activity-feed .section-title {
  margin-bottom: 20px;
  color: #333;
  font-size: 18px;
  font-weight: 600;
}

.activity-feed .activities {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.activity-feed .activity-item {
  padding: 15px;
  border-left: 4px solid #1976D2;
  background-color: #f9f9f9;
  border-radius: 0 8px 8px 0;
}

.activity-feed .activity-date {
  font-size: 14px;
  color: #666;
  margin-bottom: 10px;
}

.activity-feed .activity-content {
  font-size: 16px;
  color: #333;
  margin-bottom: 15px;
  line-height: 1.4;
}

.activity-feed .activity-actions {
  display: flex;
  gap: 10px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .collector-overview {
    grid-template-columns: 1fr;
  }
  
  .collections-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .collector-header {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }
  
  .collector-header .header-actions {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .collections-grid {
    grid-template-columns: 1fr;
  }
  
  .activity-feed .activity-actions {
    flex-direction: column;
  }
  
  .activity-feed .activity-actions .el-button {
    width: 100%;
  }
}

/* 交易相关样式 */
.trade-section {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.trade-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #e0e0e0;
}

.trade-title {
  display: flex;
  align-items: center;
  gap: 15px;
}

.trade-title h3 {
  margin: 0;
  color: #333;
  font-size: 20px;
  font-weight: 600;
}

.trade-stats {
  margin-bottom: 30px;
}

.trade-stats h4 {
  margin-bottom: 15px;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.stat-item {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  border: 1px solid #e0e0e0;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.stat-amount {
  font-size: 16px;
  color: #666;
}

.stat-status {
  font-size: 12px;
  margin-top: 5px;
}

.quick-actions {
  margin-bottom: 30px;
}

.quick-actions h4 {
  margin-bottom: 15px;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 15px;
}

.actions-grid .el-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  padding: 15px;
  text-align: center;
}

.action-desc {
  font-size: 12px;
  margin-top: 5px;
}

.trade-flow {
  margin-bottom: 30px;
}

.flow-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.flow-header h4 {
  margin: 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

.filter-section {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 8px;
}

.filter-row {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.filter-row:last-child {
  margin-bottom: 0;
}

.trade-records {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.trade-record {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.record-date {
  font-size: 14px;
  color: #666;
}

.record-amount {
  font-size: 18px;
  font-weight: bold;
}

.record-divider {
  height: 1px;
  background-color: #e0e0e0;
  margin: 15px 0;
}

.record-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.record-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.record-details {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  font-size: 14px;
  color: #666;
}

.detail-item {
  display: inline-block;
}

.record-status {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  font-size: 14px;
  color: #666;
}

.status-item {
  display: inline-block;
}

.record-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.profit-analysis {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.profit-analysis h4 {
  margin-bottom: 20px;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

.analysis-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.analysis-item {
  background-color: white;
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.analysis-item.full-width {
  grid-column: span 2;
}

.analysis-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.analysis-value {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

/* 行情页面样式 */
.market-section {
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

/* 塑料小人指数 */
.market-index {
  margin-bottom: 30px;
  padding: 20px;
  background-color: #f5f5f5;
  border-radius: 8px;
}

.index-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.index-header h3 {
  margin: 0;
  color: #333;
  font-size: 20px;
  font-weight: 600;
}

.index-stats {
  display: flex;
  gap: 20px;
}

.index-stats .stat-item {
  text-align: center;
}

.index-stats .stat-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.index-stats .stat-value {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.index-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.index-main {
  flex: 1;
}

.index-value {
  font-size: 36px;
  font-weight: 700;
  color: #333;
  margin-bottom: 10px;
}

.index-change {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 10px;
}

.index-volume {
  font-size: 14px;
  color: #666;
}

.index-limits {
  text-align: right;
}

.limit-item {
  margin-bottom: 10px;
  font-size: 14px;
}

.limit-label {
  color: #666;
  margin-right: 10px;
}

.limit-stocks {
  color: #333;
  font-weight: 500;
}

/* K线图 */
.kline-section {
  margin-bottom: 30px;
}

.kline-header {
  margin-bottom: 15px;
}

.kline-tabs {
  display: flex;
  gap: 10px;
}

.kline-tabs .el-button.active {
  background-color: #4CAF50;
  color: white;
}

.kline-chart-container {
  position: relative;
  background-color: #f5f5f5;
  border-radius: 8px;
  padding: 20px;
}

.kline-chart {
  width: 100%;
  height: 300px;
  margin-bottom: 15px;
  background: linear-gradient(to bottom, #f0f9ff 0%, #ffffff 100%);
  border-radius: 4px;
  overflow: hidden;
}

.kline-indicators {
  display: flex;
  gap: 30px;
  padding-top: 15px;
  border-top: 1px solid #e0e0e0;
}

.indicator-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.indicator-label {
  font-size: 14px;
  color: #666;
}

.indicator-value {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.indicator-value.warning {
  color: #ff9800;
}

/* 板块涨幅排行 */
.sector-ranking {
  margin-bottom: 30px;
}

.sector-list {
  background-color: #f5f5f5;
  border-radius: 8px;
  padding: 20px;
}

.sector-item {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e0e0e0;
}

.sector-item:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.sector-rank {
  width: 40px;
  font-size: 18px;
  font-weight: 600;
  color: #666;
}

.sector-info {
  flex: 1;
}

.sector-name {
  font-size: 16px;
  font-weight: 500;
  color: #333;
  margin-bottom: 5px;
}

.sector-stocks {
  font-size: 14px;
  color: #666;
}

.sector-change {
  font-size: 16px;
  font-weight: 600;
  min-width: 80px;
  text-align: right;
}

/* 我的自选股 */
.watchlist-section {
  margin-bottom: 30px;
}

.watchlist-table {
  background-color: #f5f5f5;
  border-radius: 8px;
  padding: 20px;
  overflow-x: auto;
}

.watchlist-table table {
  width: 100%;
  border-collapse: collapse;
}

.watchlist-table th,
.watchlist-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
}

.watchlist-table th {
  background-color: #e3f2fd;
  font-weight: 600;
  color: #1976D2;
}

.watchlist-table tr:hover {
  background-color: #e3f2fd;
}

/* 智能投研 */
.research-section {
  margin-bottom: 30px;
}

.research-card {
  background-color: #f5f5f5;
  border-radius: 8px;
  padding: 20px;
}

.research-item {
  display: flex;
  margin-bottom: 15px;
  align-items: flex-start;
}

.research-label {
  width: 100px;
  font-size: 14px;
  font-weight: 600;
  color: #666;
}

.research-value {
  flex: 1;
  font-size: 14px;
  color: #333;
  line-height: 1.5;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .main-content {
    grid-template-columns: 1fr;
  }
  
  .asset-overview {
    flex-direction: column;
    gap: 15px;
  }
  
  .index-comparison {
    flex-direction: column;
    gap: 15px;
  }
  
  .orders-container {
    margin-left: 20px;
    margin-right: 20px;
  }
  
  .collector-mode .empty-state {
    padding: 40px 20px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .actions-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .analysis-grid {
    grid-template-columns: 1fr;
  }
  
  .analysis-item.full-width {
    grid-column: span 1;
  }
}

@media (max-width: 768px) {
  .actions-grid {
    grid-template-columns: 1fr;
  }
  
  .trade-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .trade-title {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .record-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .record-details {
    flex-direction: column;
    gap: 5px;
  }
  
  .record-status {
    flex-direction: column;
    gap: 5px;
  }
  
  .record-actions {
    flex-direction: column;
  }
  
  .record-actions .el-button {
    width: 100%;
  }
}
</style>