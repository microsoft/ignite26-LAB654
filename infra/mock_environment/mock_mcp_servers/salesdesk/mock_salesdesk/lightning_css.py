"""Stylesheet for the viewer, in the SalesDesk look."""

CSS = """
*{box-sizing:border-box}
html,body{margin:0}
body{font-family:-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;font-size:13px;line-height:1.5;color:#181818;
background:#cdc3ee linear-gradient(180deg,#cdc3ee 0,#dcd5f3 220px,#ebe7f8 520px,#f4f2fa 900px) no-repeat;min-height:100vh}
a{color:#5b21b6;text-decoration:none}
a:hover{text-decoration:underline;color:#4c1d95}
button{font:inherit}
.gh{position:sticky;top:0;z-index:20}
.gh-top{height:50px;background:#fff;display:flex;align-items:center;padding:0 12px;gap:12px;border-bottom:1px solid #e5e5e5}
.logo{display:flex;align-items:center;width:200px}
.search{flex:0 1 560px;margin:0 auto;position:relative}
.search input{width:100%;height:32px;border:1px solid #c9c9c9;border-radius:4px;padding:0 12px 0 34px;font:inherit;
background:#fff;color:#181818}
.search input:focus{outline:none;border-color:#8b5cf6;box-shadow:0 0 3px #6d28d9}
.search svg{position:absolute;left:11px;top:9px}
.gh-icons{display:flex;align-items:center;gap:6px;width:200px;justify-content:flex-end}
.gh-ico{width:28px;height:28px;border-radius:4px;display:grid;place-items:center;color:#747474}
.gh-ico:hover{background:#f3f3f3}
.avatar{width:32px;height:32px;border-radius:50%;background:#2e1065;color:#fff;display:grid;place-items:center;
font-size:12px;font-weight:700;margin-left:6px}
.ctx{height:40px;background:#fff;display:flex;align-items:stretch;border-bottom:3px solid #6d28d9;padding-left:6px;
box-shadow:0 2px 3px rgba(0,0,0,.12)}
.waffle{display:grid;place-items:center;width:40px}
.waffle i{display:grid;grid-template-columns:repeat(3,4px);gap:3px}
.waffle b{width:4px;height:4px;border-radius:50%;background:#747474;display:block}
.appname{font-size:18px;font-weight:400;display:flex;align-items:center;padding:0 22px 0 6px;color:#181818}
.tab{display:flex;align-items:center;padding:0 12px;color:#181818;font-size:13px;position:relative;white-space:nowrap}
.tab:hover{background:#f3f3f3;text-decoration:none;color:#181818}
.tab.on{background:#f3f3f3;font-weight:400}
.tab.on:before{content:"";position:absolute;left:0;right:0;top:0;height:3px;background:#6d28d9}
.tab .chev{margin-left:8px;color:#747474;font-size:9px}
.notice{margin:12px 12px 0;background:#fe9339;color:#181818;border-radius:4px;padding:8px 14px;
display:flex;gap:10px;align-items:center;box-shadow:0 2px 2px rgba(0,0,0,.1)}
.notice.info{background:#747474;color:#fff}
main{padding:12px}
.card{background:#fff;border:1px solid #c9c9c9;border-radius:4px;box-shadow:0 2px 2px 0 rgba(0,0,0,.1)}
.card+.card,.stack>*+*{margin-top:12px}
.card-h{display:flex;align-items:center;gap:10px;padding:12px 16px 4px}
.card-h h2{margin:0;font-size:14px;font-weight:700;flex:1;line-height:1.25}
.card-h h2 a{color:#181818}
.card-b{padding:8px 16px 14px}
.card-f{border-top:1px solid #e5e5e5;text-align:center;padding:10px;font-size:13px}
.icon{display:inline-grid;place-items:center;border-radius:4px;flex:none}
.icon svg{display:block}
.btn{display:inline-flex;align-items:center;gap:6px;height:32px;padding:0 16px;border:1px solid #c9c9c9;
background:#fff;color:#6d28d9;border-radius:4px;cursor:default;white-space:nowrap;font-size:13px}
.btn:hover{background:#f3f3f3}
.btn.brand{background:#6d28d9;border-color:#6d28d9;color:#fff}
.btngrp{display:inline-flex}
.btngrp .btn{border-radius:0;margin-left:-1px}
.btngrp .btn:first-child{border-radius:4px 0 0 4px;margin-left:0}
.btngrp .btn:last-child{border-radius:0 4px 4px 0}
.btn.icn{padding:0 8px}
.ph{padding:14px 16px}
.ph-row{display:flex;align-items:flex-start;gap:12px}
.ph-t{flex:1;min-width:0}
.ph-t small{display:block;font-size:13px;color:#181818;line-height:1.2}
.ph-t h1{margin:2px 0 0;font-size:18px;font-weight:700;line-height:1.25}
.ph-t h1 .dd{font-size:11px;color:#747474;margin-left:6px;vertical-align:middle}
.ph-meta{margin-top:10px;font-size:12px;color:#444}
.hl{display:flex;flex-wrap:wrap;gap:6px 36px;margin-top:14px;padding-top:4px}
.hl div{min-width:0;max-width:260px}
.hl dt{font-size:12px;color:#444;margin:0}
.hl dd{margin:0;font-size:13px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.cols{display:grid;grid-template-columns:minmax(0,2fr) minmax(0,1fr);gap:12px;margin-top:12px;align-items:start}
.cols.full{grid-template-columns:minmax(0,1fr)}
.tabs{display:flex;gap:4px;border-bottom:1px solid #e5e5e5;padding:0 16px}
.tabs a{padding:12px 10px 10px;color:#181818;font-size:13px;border-bottom:3px solid transparent;margin-bottom:-1px}
.tabs a:hover{text-decoration:none;border-bottom-color:#c9c9c9}
.tabs a.on{border-bottom-color:#6d28d9;font-weight:700}
.sec{margin:12px 16px 0}
.sec-h{background:#f3f3f3;border-radius:4px;padding:5px 10px;font-size:14px;font-weight:400;display:flex;gap:8px;
align-items:center}
.sec-h:before{content:"\\25BE";color:#747474;font-size:11px}
.form{display:grid;grid-template-columns:1fr 1fr;column-gap:24px;padding:4px 4px 6px}
.fld{border-bottom:1px solid #e5e5e5;padding:6px 26px 4px 4px;position:relative;min-height:46px}
.fld.wide{grid-column:1/-1}
.fld label{display:block;font-size:12px;color:#444;line-height:1.4}
.fld .v{font-size:14px;min-height:20px;word-wrap:break-word}
.fld:after{content:"\\270E";position:absolute;right:6px;bottom:6px;color:#aeaeae;font-size:12px;opacity:0}
.fld:hover:after{opacity:1}
.fld .sub{font-size:12px;color:#444}
.chk{display:inline-grid;place-items:center;width:16px;height:16px;border:1px solid #c9c9c9;border-radius:2px;
font-size:11px;color:#6d28d9;vertical-align:middle}
.path{display:flex;align-items:center;gap:12px;padding:12px 16px}
.path ol{list-style:none;margin:0;padding:0;display:flex;flex:1;min-width:0}
.path li{flex:1;min-width:0;height:32px;display:flex;align-items:center;justify-content:center;font-size:13px;
background:#e5e5e5;color:#181818;margin-left:-6px;padding:0 14px 0 20px;
clip-path:polygon(0 0,calc(100% - 12px) 0,100% 50%,calc(100% - 12px) 100%,0 100%,12px 50%)}
.path li:first-child{margin-left:0;border-radius:16px 0 0 16px;clip-path:polygon(0 0,calc(100% - 12px) 0,100% 50%,calc(100% - 12px) 100%,0 100%)}
.path li:last-child{border-radius:0 16px 16px 0;clip-path:polygon(0 0,100% 0,100% 100%,0 100%,12px 50%)}
.path li span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.path li.done{background:#3ba755;color:#fff}
.path li.cur{background:#4c1d95;color:#fff;font-weight:700}
.path li.won{background:#3ba755;color:#fff;font-weight:700}
.path li.lost{background:#ba0517;color:#fff;font-weight:700}
.path-keys{display:flex;gap:40px;padding:0 16px 12px;font-size:12px;color:#444}
.path-keys b{display:block;font-size:13px;color:#181818;font-weight:400}
.rl .card-h h2 a{color:#181818}
.tile{display:flex;gap:10px;padding:8px 0;border-top:1px solid #f3f3f3}
.tile:first-child{border-top:0}
.tile dl{margin:2px 0 0;display:grid;grid-template-columns:auto 1fr;gap:0 8px;font-size:12px}
.tile dt{color:#444}
.tile dd{margin:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.tile .nm{font-size:13px}
.empty{color:#444;padding:6px 0 2px;font-size:13px}
table.dt{width:100%;border-collapse:collapse;font-size:13px;table-layout:auto}
table.dt th{background:#f3f3f3;color:#444;font-weight:700;font-size:12px;text-align:left;padding:7px 8px;
border-bottom:1px solid #c9c9c9;border-right:1px solid #e5e5e5;white-space:nowrap}
table.dt th .ar{color:#747474;font-size:10px;margin-left:4px}
table.dt td{padding:7px 8px;border-bottom:1px solid #e5e5e5;white-space:nowrap;max-width:320px;overflow:hidden;
text-overflow:ellipsis}
table.dt tr:hover td{background:#f3f3f3}
table.dt td.num,table.dt th.num{text-align:right}
table.dt td.rn{color:#444;width:36px;text-align:right}
table.dt td.ck,table.dt th.ck{width:32px;text-align:center}
.cb{display:inline-block;width:14px;height:14px;border:1px solid #c9c9c9;border-radius:2px;vertical-align:middle;
background:#fff}
.rowact{display:inline-grid;place-items:center;width:22px;height:22px;border:1px solid #c9c9c9;border-radius:4px;
color:#747474;font-size:9px}
.lv{padding:0}
.lv .ph{border-bottom:1px solid #e5e5e5}
.tl{list-style:none;margin:0;padding:0}
.tl-g{display:flex;align-items:center;gap:8px;margin:14px 0 6px;font-size:13px;font-weight:700}
.tl-g:after{content:"";flex:1;border-top:1px solid #e5e5e5}
.tl li{display:flex;gap:10px;position:relative;padding:4px 0 12px}
.tl li:before{content:"";position:absolute;left:11px;top:30px;bottom:0;width:2px;background:#dddbda}
.tl li:last-child:before{display:none}
.tl .tx{flex:1;min-width:0}
.tl .ttl{display:flex;justify-content:space-between;gap:12px}
.tl .ttl a{font-weight:400}
.tl .dt2{color:#444;font-size:12px;white-space:nowrap}
.tl .sub{font-size:12px;color:#444}
.tl .desc{margin-top:6px;font-size:12px;color:#181818;background:#f3f3f3;border-radius:4px;padding:6px 10px;
white-space:pre-line}
.composer{display:flex;gap:6px;flex-wrap:wrap;padding:12px 16px 4px}
.filters{display:flex;justify-content:space-between;font-size:12px;color:#444;padding:8px 16px 0}
.home{display:grid;grid-template-columns:minmax(0,2fr) minmax(0,1fr);gap:12px}
.qp-sum{display:flex;gap:28px;padding:4px 16px 0}
.qp-sum div{font-size:12px;color:#444}
.qp-sum b{display:block;font-size:20px;color:#181818;font-weight:400;line-height:1.3}
.legend{display:flex;gap:16px;justify-content:center;font-size:12px;color:#444;padding:2px 0 8px}
.legend i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px;vertical-align:-1px}
.free{display:flex;gap:14px;align-items:center;color:#444;padding:10px 0}
.deal{display:grid;grid-template-columns:auto 1fr auto;gap:2px 10px;padding:10px 0;border-top:1px solid #f3f3f3;
align-items:center}
.deal:first-child{border-top:0}
.deal .m{font-size:12px;color:#444}
.deal .amt{text-align:right;font-size:13px}
.assist{display:flex;gap:10px;padding:8px 0;border-top:1px solid #f3f3f3}
.assist:first-child{border-top:0}
.dash{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-top:12px}
.dash .span2{grid-column:span 2}
.dash>.card+.card{margin-top:0}
.dash svg.chart{max-height:280px}
.dash .gauge svg.chart{max-height:200px}
.comp{display:flex;flex-direction:column}
.comp .card-h h2{font-size:14px;font-weight:400}
.comp .card-b{flex:1;display:flex;flex-direction:column;justify-content:center;min-width:0;overflow-x:auto}
.comp .card-b:has(>table.dt){justify-content:flex-start}
.comp .card-f{text-align:left;font-size:12px}
.metric{font-size:42px;text-align:center;color:#181818;padding:22px 0 12px;font-weight:300}
.metric small{display:block;font-size:12px;color:#444;font-weight:400}
.chart text{font-family:inherit}
.search-res h2{font-size:16px;margin:0}
.nf{padding:40px 20px;text-align:center}
.nf h1{font-size:20px;margin:12px 0 6px;font-weight:400}
footer{color:#444;font-size:11px;text-align:center;padding:14px}
"""
