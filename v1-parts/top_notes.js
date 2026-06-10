  const TOP_NOTES = [
    {title: "彩虹糖x心动小镇联名糖果礼盒联动开启！", cat: "糖果零食", ctr: 31.3, tagCtr: 88.6, imp: 48682, url: "https://www.xiaohongshu.com/explore/6a1127c20000000035024146"},
    {title: "你抄袭的速度永远赶不上我爸创新的速度!", cat: "面点速食", ctr: 25.7, tagCtr: 23.1, imp: 6036, url: "https://www.xiaohongshu.com/explore/6a0c1f050000000007026baf"},
    {title: "实在是忍不住发布（客返图）拍的实在美丽！", cat: "糕点", ctr: 26.0, tagCtr: 16.0, imp: 43691, url: "https://www.xiaohongshu.com/explore/6a0f169200000000070275c0"},
    {title: "宠粉福利🎁巧克力花生酱免费尝❗", cat: "调味品", ctr: 25.1, tagCtr: 16.6, imp: 15692, url: "https://www.xiaohongshu.com/explore/6a0ede7e000000000702029c"},
    {title: "生意惨淡的原因找到了😂😂😂", cat: "速食", ctr: 28.8, tagCtr: 11.1, imp: 198716, url: "https://www.xiaohongshu.com/explore/6a0b3aa6000000003502ff84"},
    {title: "咱就是说龙华的这个玉米粽子征服了我的嘴？", cat: "糕点", ctr: 30.2, tagCtr: 15.0, imp: 4264, url: "https://www.xiaohongshu.com/explore/6a0d408f0000000006033a27"},
    {title: "免费的赠品就是香🥰", cat: "咖啡", ctr: 27.2, tagCtr: 10.8, imp: 47961, url: "https://www.xiaohongshu.com/explore/6a06979c000000000702ab67"},
    {title: "我们家夏天餐桌上真的少不了这罐油焖笋‼️", cat: "蜜饯果干", ctr: 27.1, tagCtr: 11.6, imp: 3229, url: "https://www.xiaohongshu.com/explore/6a1023e8000000003700d93b"},
    {title: "🫠遇到裸寄的了😰", cat: "糕点", ctr: 25.4, tagCtr: 8.2, imp: 116148, url: "https://www.xiaohongshu.com/explore/6a115bb500000000360192c5"},
    {title: "收到货发现出水，渣渣的，辣舌头别扔啊！", cat: "糕点", ctr: 24.9, tagCtr: 10.4, imp: 11254, url: "https://www.xiaohongshu.com/explore/6a11069300000000060320cd"},
    {title: "吃完可以谎报体重了，热量太低了。。。", cat: "调味品", ctr: 23.9, tagCtr: 9.3, imp: 25341, url: "https://www.xiaohongshu.com/explore/6a07f2a30000000035033494"},
    {title: "没想到遇到裸寄了... 🥺", cat: "面点速食", ctr: 24.6, tagCtr: 9.5, imp: 7871, url: "https://www.xiaohongshu.com/explore/6a1170d40000000006030814"},
    {title: "胖东来茶叶品质可靠包装精美|可永远相信！", cat: "白茶", ctr: 24.1, tagCtr: 10.1, imp: 4214, url: "https://www.xiaohongshu.com/explore/6a04523f0000000006031a64"},
    {title: "（已排雷）薏米水22天，比帕梅啦还🐮", cat: "养生茶", ctr: 24.4, tagCtr: 8.0, imp: 25092, url: "https://www.xiaohongshu.com/explore/6a03da89000000000803312f"},
    {title: "妈呀！喝了真的有用", cat: "冲饮品", ctr: 25.8, tagCtr: 7.1, imp: 10707, url: "https://www.xiaohongshu.com/explore/6a047d6a00000000350281c7"},
    {title: "星愿薯饼——星星脸暴击治愈力", cat: "糕点", ctr: 24.6, tagCtr: 6.6, imp: 28742, url: "https://www.xiaohongshu.com/explore/6a0d20c50000000035021c87"},
    {title: "8:2香肠，左划帮你蒸熟😅", cat: "南北干货", ctr: 26.7, tagCtr: 4.9, imp: 216330, url: "https://www.xiaohongshu.com/explore/6a069e0600000000360324fb"},
    {title: "婆婆又煮了一锅｜我手把手教你做七宝水✨", cat: "中式滋补", ctr: 29.4, tagCtr: 4.1, imp: 62961, url: "https://www.xiaohongshu.com/explore/6a0468750000000036000d0e"},
    {title: "其实减脂期总饿的人都有一个明显共性。。。", cat: "米面杂粮", ctr: 24.9, tagCtr: 5.6, imp: 11972, url: "https://www.xiaohongshu.com/explore/6a09b1fe000000003501ce31"},
    {title: "山姆新品｜泰式奶茶翡翠沙喝到啦！！！", cat: "饮料", ctr: 35.5, tagCtr: 4.2, imp: 5852, url: "https://www.xiaohongshu.com/explore/6a0d7a63000000003700d0d1"},
  ];

  function renderTopNotes() {
    const grid = document.getElementById('topNotesGrid');
    if (!grid) return;
    const rankClass = (i) => i === 0 ? 'gold' : i === 1 ? 'silver' : i === 2 ? 'bronze' : '';
    grid.innerHTML = TOP_NOTES.map((n, i) => `
      <a class="top-note-row" href="${n.url}" target="_blank" rel="noopener">
        <div class="top-note-rank ${rankClass(i)}">${i + 1}</div>
        <div class="top-note-title">${n.title}</div>
        <div class="top-note-cat">${n.cat}</div>
        <div class="top-note-metrics">
          <div class="top-note-metric">封面CTR <span>${n.ctr}%</span></div>
          <div class="top-note-metric">商卡CTR <span>${n.tagCtr}%</span></div>
          <div class="top-note-metric">曝光 <span>${n.imp >= 10000 ? (n.imp/10000).toFixed(1)+'万' : n.imp.toLocaleString()}</span></div>
        </div>
        <div class="top-note-arrow">→</div>
      </a>
    `).join('');
  }
  renderTopNotes();

