#!/usr/bin/env python3
"""
WeasyPrint 专用渲染脚本
使用 ai-sector-briefing-weasyprint.html 模板（纯静态，无需 JavaScript）
"""
import sys, json, re
from pathlib import Path

def extract_data(html_path):
    """从动态 HTML 中提取 DATA 对象"""
    html = Path(html_path).read_text(encoding='utf-8')
    match = re.search(r'const\s+DATA\s*=\s*(\{.*?\n\});', html, re.DOTALL)
    if not match:
        return None
    return json.loads(match.group(1))

def get_color_class(pct):
    """根据百分位获取颜色类"""
    if pct >= 80:
        return 'red'
    if pct >= 50:
        return 'yellow'
    return 'green'

def get_bar_bg(pct):
    """获取进度条背景色（纯色替代渐变）"""
    if pct >= 80:
        return 'var(--red)'
    if pct >= 50:
        return 'var(--yellow)'
    return 'var(--green)'

def format_change(v):
    """格式化涨跌幅"""
    return f"{v:+.1f}%"

def format_flow(v):
    """格式化资金流向"""
    return f"{v:+.1f}亿"

def get_sector_status(pct):
    """获取估值状态描述"""
    if pct >= 80:
        return '高估'
    if pct >= 65:
        return '中高'
    if pct >= 35:
        return '正常'
    if pct >= 20:
        return '偏低'
    return '低估'

def get_fear_ring_class(value):
    """获取恐惧贪婪圆环颜色类"""
    if value >= 75:
        return 'red'
    if value >= 50:
        return 'orange'
    if value >= 25:
        return 'yellow'
    return 'green'

def get_fear_color(value):
    """获取恐惧贪婪数值颜色"""
    if value >= 75:
        return 'var(--red)'
    if value >= 50:
        return 'var(--yellow)'
    if value >= 25:
        return 'var(--orange)'
    return 'var(--green)'

def get_signal_badge(pct):
    """获取信号标签"""
    if pct >= 80:
        return ('sell', '减仓')
    if pct >= 50:
        return ('hold', '持有')
    return ('buy', '建仓')

def get_icon_class(pct):
    """获取图标颜色类"""
    if pct >= 80:
        return 'red'
    if pct >= 50:
        return 'yellow'
    return 'green'

def get_change_color(v):
    """获取涨跌幅颜色 涨绿跌红"""
    if v >= 0:
        return 'var(--green)'
    return 'var(--red)'

def get_news_tag_class(impact):
    """获取资讯标签类"""
    if impact == '利好':
        return 'up'
    if impact == '利空':
        return 'down'
    return 'mid'

def build_context(data):
    """构建模板上下文"""
    ctx = {}
    
    # 基本信息（移除emoji，避免PDF渲染成方块）
    ctx['date'] = data.get('date', '')
    ctx['signal_level'] = data.get('signal_level', 'warn')
    signal_text = data.get('signal_text', '中性偏谨慎')
    # 移除emoji前缀
    signal_text = signal_text.replace('🔴', '').replace('🟡', '').replace('🟢', '').strip()
    ctx['signal_text'] = signal_text
    
    # 估值温度计
    ctx['indices'] = []
    for idx in data.get('indices', []):
        pct = idx.get('pe_pct', 0)
        ctx['indices'].append({
            'name': idx.get('name', ''),
            'pe_pct': pct,
            'warning': pct >= 80,
            'color': 'var(--red)' if pct >= 80 else ('var(--yellow)' if pct >= 50 else 'var(--green)'),
            'bar_class': get_color_class(pct)
        })
    
    # 恐惧贪婪指数
    fg = data.get('fear_greed', {})
    fv = fg.get('value', 50)
    ctx['fear_value'] = fv
    ctx['fear_zone'] = fg.get('zone', '中性')
    ctx['fear_color'] = get_fear_color(fv)
    ctx['fear_ring_class'] = get_fear_ring_class(fv)
    
    # 资金流向
    fl = data.get('flow', {})
    ctx['north_1d'] = format_flow(fl.get('north_1d', 0))
    ctx['north_5d'] = format_flow(fl.get('north_5d', 0))
    ctx['north_20d'] = format_flow(fl.get('north_20d', 0))
    ctx['main_1d'] = format_flow(fl.get('main_1d', 0))
    
    # AI产业链（按层分组）
    layers = {
        'up': {'name': '上游 · 算力基础设施', 'color': 'var(--blue)', 'bg': 'var(--blue)', 'tip': '→ ETF为主，费率低适合波段'},
        'mid': {'name': '中游 · 模型与平台', 'color': 'var(--purple)', 'bg': 'var(--purple)', 'tip': '→ 主动型为主，精选个股'},
        'down': {'name': '下游 · 应用落地', 'color': 'var(--green)', 'bg': 'var(--green)', 'tip': '→ 主动型为主，挖掘黑马'}
    }
    
    ctx['layer_sections'] = []
    for layer_key, layer_info in layers.items():
        sectors = [s for s in data.get('sectors', []) if s.get('layer') == layer_key]
        if not sectors:
            continue
        
        section = {
            'layer_name': layer_info['name'],
            'layer_color': layer_info['color'],
            'sectors': []
        }
        for s in sectors:
            chg = s.get('change', 0)
            pct = s.get('pe_pct', 0)
            section['sectors'].append({
                'name': s.get('name', ''),
                'change': format_change(chg),
                'change_color': get_change_color(chg),
                'pe_pct': pct,
                'bar_bg': get_bar_bg(pct),
                'status': get_sector_status(pct)
            })
        ctx['layer_sections'].append(section)
    
    # 择时信号（取PE最高的6个）
    signals = []
    for s in data.get('sectors', []):
        pct = s.get('pe_pct', 0)
        badge_class, badge_text = get_signal_badge(pct)
        signals.append({
            'name': s.get('name', ''),
            'reason': f"PE分位{pct}%",
            'icon_class': get_icon_class(pct),
            'badge_class': badge_class,
            'badge_text': badge_text,
            'pct': pct
        })
    signals.sort(key=lambda x: x['pct'], reverse=True)
    ctx['signals'] = signals[:6]
    
    # 资讯
    ctx['news'] = []
    for n in data.get('news', []):
        ctx['news'].append({
            'impact': n.get('impact', '中性'),
            'tag_class': get_news_tag_class(n.get('impact', '中性')),
            'text': n.get('text', '')
        })
    
    # 推荐基金（按层分组）
    ctx['fund_sections'] = []
    for layer_key, layer_info in layers.items():
        funds = [f for f in data.get('funds', []) if f.get('layer') == layer_key]
        if not funds:
            continue
        
        # 同层级按近一年收益率从高到低排序
        funds.sort(key=lambda x: x.get('return_1y', 0) or 0, reverse=True)
        
        # 计算该层平均PE作为信号参考
        layer_sectors = [s for s in data.get('sectors', []) if s.get('layer') == layer_key]
        avg_pe = sum(s.get('pe_pct', 0) for s in layer_sectors) / len(layer_sectors) if layer_sectors else 50
        sig_class, sig_text = get_signal_badge(avg_pe)
        
        section = {
            'layer_name': layer_info['name'],
            'layer_color': layer_info['color'],
            'layer_bg': layer_info['bg'],
            'layer_tip': layer_info['tip'],
            'funds': []
        }
        for f in funds:
            # 判断是否是新基金（return_1y 为 0 或 None 视为新上）
            return_1y = f.get('return_1y')
            is_new = return_1y is None or return_1y == 0
            section['funds'].append({
                'name': f.get('name', ''),
                'code': f.get('code', ''),
                'type': f.get('type', ''),
                'return_1y': return_1y if not is_new else None,
                'return_period': '近1年' if not is_new else None,
                'is_new': is_new,
                'sig_class': sig_class,
                'sig_text': sig_text
            })
        ctx['fund_sections'].append(section)
    
    # 操作建议（移除emoji，避免PDF渲染成方块）
    ctx['advice_title'] = data.get('advice_title', '核心策略')
    advice = data.get('advice', '')
    # 替换emoji为符号
    advice = advice.replace('🔹', '•').replace('🔸', '•').replace('▸', '•')
    ctx['advice'] = advice
    ctx['footer_text'] = data.get('footer_text', '数据来源：公开市场信息')
    
    return ctx

def render_template(template_path, context):
    """简单的模板渲染（支持嵌套循环 {{#list}}...{{/list}} 和条件 {{#if key}}...{{/if}}）"""
    template = Path(template_path).read_text(encoding='utf-8')
    
    def render(text, data):
        """递归渲染模板"""
        result = text
        
        # 先处理条件 {{#if key}}...{{/if}}
        def render_cond(match):
            key = match.group(1)
            inner = match.group(2)
            if data.get(key):
                return render(inner, data)
            return ''
        
        result = re.sub(r'\{\{#if (\w+)\}\}(.*?)\{\{/if\}\}', render_cond, result, flags=re.DOTALL)
        
        # 处理 {{#key}}...{{/key}} - 列表循环或布尔条件
        def render_section(match):
            key = match.group(1)
            inner = match.group(2)
            val = data.get(key)
            # 列表：循环渲染
            if isinstance(val, list):
                result = []
                for item in val:
                    rendered = render(inner, item)
                    result.append(rendered)
                return ''.join(result)
            # 布尔值或真值：条件渲染
            elif val:
                return render(inner, data)
            # 假值：不渲染
            else:
                return ''
        
        result = re.sub(r'\{\{#(\w+)\}\}(.*?)\{\{/\1\}\}', render_section, result, flags=re.DOTALL)
        
        # 处理反义条件 {{^var}}...{{/var}}（当 var 为空或不存在时显示）
        def render_inverse(match):
            key = match.group(1)
            inner = match.group(2)
            val = data.get(key)
            # 空列表、None、空字符串都视为空
            is_empty = (val is None or val == '' or 
                       (isinstance(val, list) and len(val) == 0))
            if is_empty:
                return render(inner, data)
            return ''
        
        result = re.sub(r'\{\{\^(\w+)\}\}(.*?)\{\{/\1\}\}', render_inverse, result, flags=re.DOTALL)
        
        # 最后处理变量
        def replace_var(m):
            # m.group(1) 是 {{{key}}} 中的 key
            # m.group(2) 是 {{key}} 中的 key
            key = m.group(1) if m.group(1) is not None else m.group(2)
            val = data.get(key, '')
            return str(val)
        
        result = re.sub(r'\{\{\{(\w+)\}\}\}|\{\{(\w+)\}\}', replace_var, result)
        return result
    
    return render(template, context)

def html_to_pdf(html_path, output_path):
    """主入口：从动态 HTML 提取数据，渲染 WeasyPrint 模板，生成 PDF"""
    # 提取数据
    data = extract_data(html_path)
    if not data:
        print("错误：无法从 HTML 中提取 DATA 对象")
        sys.exit(1)
    
    # 构建上下文
    context = build_context(data)
    
    # 渲染模板 - 从多个可能的位置查找
    script_dir = Path(__file__).parent
    skill_dir = script_dir.parent
    template_paths = [
        skill_dir / 'templates' / 'ai-sector-briefing-weasyprint.html',
        script_dir / 'templates' / 'ai-sector-briefing-weasyprint.html',
        Path(html_path).parent / 'ai-sector-briefing-weasyprint.html',
        Path(html_path).parent / 'templates' / 'ai-sector-briefing-weasyprint.html'
    ]
    
    template_path = None
    for tp in template_paths:
        if tp.exists():
            template_path = tp
            break
    
    if not template_path:
        print(f"错误：找不到模板文件 ai-sector-briefing-weasyprint.html")
        print(f"搜索路径: {[str(p) for p in template_paths]}")
        sys.exit(1)
    
    static_html = render_template(template_path, context)
    
    # 生成 PDF（无边距，背景色填满整个页面）
    from weasyprint import HTML, CSS
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # 页面无边距，让 body 背景填满整个页面
    page_css = CSS(string='''
        @page {
            size: A4;
            margin: 0;
        }
    ''')
    HTML(string=static_html).write_pdf(output_path, stylesheets=[page_css])
    print(f"PDF: {output_path}")

def main():
    if len(sys.argv) != 3:
        print("用法: python scripts/render_pdf_simple.py <动态html> <pdf>")
        print("说明: 从动态 HTML 提取 DATA，使用 weasyprint 模板生成 PDF")
        sys.exit(1)
    html_to_pdf(sys.argv[1], sys.argv[2])

if __name__ == '__main__':
    main()
