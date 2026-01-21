document.getElementById('formulaForm').addEventListener('submit', async (e) => {
  e.preventDefault();

  const num1 = document.getElementById('num1').value;
  const num2 = document.getElementById('num2').value;
  const highQuality = document.getElementById('highQuality').checked;
  const status = document.getElementById('status');
  const result = document.getElementById('result');

  if (!num1 || !num2 || num1 <= 0 || num2 <= 0) {
    alert('请输入正整数！');
    return;
  }

  status.textContent = '⏳ 正在渲染动画...（可能需要 10-60 秒）';
  result.innerHTML = '';
  document.querySelector('button').disabled = true;

  try {
    // 👇 修改这里：指向你的公网 API 地址
    const API_BASE = 'http://your-server-ip:5000'; // ← 替换为你的真实服务器地址

    const res = await fetch(`${API_BASE}/api/render`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        num1: parseInt(num1), 
        num2: parseInt(num2), 
        high_quality: highQuality 
      })
    });

    const data = await res.json();
    
    if (res.ok) {
      status.textContent = '✅ 渲染完成！';
      result.innerHTML = `
        <video controls>
          <source src="${API_BASE}${data.video_url}" type="video/mp4">
          您的浏览器不支持视频播放。
        </video><br>
        <a href="${API_BASE}${data.download_url}" download>📥 下载视频</a>
      `;
    } else {
      throw new Error(data.error || '未知错误');
    }
  } catch (err) {
    console.error(err);
    status.textContent = '❌ 错误: ' + (err.message || '请求失败，请检查网络或服务器是否运行中');
  } finally {
    document.querySelector('button').disabled = false;
  }
});