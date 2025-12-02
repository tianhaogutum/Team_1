# GPX 地图功能测试指南

## 功能概述

已实现基于 GPX 数据的地图显示功能，可以：
1. 解析 GPX XML 数据
2. 在 GPX 轨迹上绘制路线
3. 自动定位 breakpoint 到轨迹上的最近点
4. 如果没有 GPX 数据，回退到固定布局

## 测试步骤

### 1. 后端 API 测试

验证 API 是否正确返回 GPX 数据：

```bash
# 启动后端服务器
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# 在另一个终端测试 API
curl http://localhost:8000/api/routes/recommendations?limit=1 | jq '.routes[0] | {id, title, gpx_data_raw: (.gpx_data_raw != null)}'
```

### 2. 前端浏览器测试

1. **启动前端开发服务器**：
   ```bash
   cd frontend
   pnpm dev
   ```

2. **打开浏览器控制台**，查看是否有 GPX 解析错误

3. **测试场景**：
   - **有 GPX 数据的路线**：应该显示 "📍 GPX Track" 标识，路线形状基于真实 GPX 轨迹
   - **没有 GPX 数据的路线**：应该使用固定布局，不显示 GPX 标识

### 3. 手动测试 GPX 解析

在浏览器控制台中运行：

```javascript
// 测试 GPX 解析
const sampleGPX = `<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1">
  <trk>
    <trkseg>
      <trkpt lat="48.1351" lon="11.5820"><ele>520</ele></trkpt>
      <trkpt lat="48.1360" lon="11.5830"><ele>525</ele></trkpt>
      <trkpt lat="48.1370" lon="11.5840"><ele>530</ele></trkpt>
    </trkseg>
  </trk>
</gpx>`;

// 导入解析函数（在浏览器中）
import { parseGPX } from '@/lib/gpx-parser';
const track = parseGPX(sampleGPX);
console.log('Parsed track:', track);
console.log('Points:', track?.points);
```

### 4. 验证功能点

#### ✅ GPX 解析
- [ ] 能正确解析包含 `<trkpt>` 的 GPX 数据
- [ ] 能提取 lat, lon, ele 信息
- [ ] 处理空或无效 GPX 数据时返回 null

#### ✅ 坐标投影
- [ ] GPS 坐标正确投影到 SVG 坐标
- [ ] 所有点都在 SVG 画布范围内
- [ ] 路径保持正确的宽高比

#### ✅ Breakpoint 定位
- [ ] 有坐标的 breakpoint 能定位到 GPX 轨迹上的最近点
- [ ] 没有坐标的 breakpoint 沿路径均匀分布
- [ ] 标签位置不会重叠

#### ✅ 路径生成
- [ ] 从 GPX 点生成平滑的 SVG 路径
- [ ] 路径正确连接所有点
- [ ] 路径样式正确（颜色、宽度等）

#### ✅ 回退机制
- [ ] 没有 GPX 数据时使用固定布局
- [ ] 没有 breakpoint 坐标时使用索引分布
- [ ] 错误处理不会导致崩溃

## 测试数据

### 示例 GPX 数据格式

```xml
<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="TrailSaga – Hogwarts Expedition Series">
  <trk>
    <name>Test Route</name>
    <trkseg>
      <trkpt lat="48.1351" lon="11.5820">
        <ele>520</ele>
      </trkpt>
      <trkpt lat="48.1360" lon="11.5830">
        <ele>525</ele>
      </trkpt>
      <!-- 更多点... -->
    </trkseg>
  </trk>
</gpx>
```

### 在数据库中添加测试 GPX 数据

```python
# 在 Python shell 中
from app.database import get_db_session
from app.models.entities import Route
from app.settings import get_settings
import asyncio

async def add_test_gpx():
    settings = get_settings()
    from app.database import init_db
    init_db(settings)
    
    async with await get_db_session() as session:
        route = await session.get(Route, 1)  # 使用你的路线 ID
        if route:
            route.gpx_data_raw = """<?xml version="1.0"?>
<gpx version="1.1">
  <trk>
    <trkseg>
      <trkpt lat="48.1351" lon="11.5820"><ele>520</ele></trkpt>
      <trkpt lat="48.1360" lon="11.5830"><ele>525</ele></trkpt>
      <trkpt lat="48.1370" lon="11.5840"><ele>530</ele></trkpt>
    </trkseg>
  </trk>
</gpx>"""
            await session.commit()
            print("✅ GPX data added")

asyncio.run(add_test_gpx())
```

## 预期行为

### 有 GPX 数据时
- 地图标题显示 "📍 GPX Track" 标识
- 路线形状反映真实 GPX 轨迹（转弯、爬升等）
- Breakpoint 位置基于 GPS 坐标，定位到轨迹上的最近点
- 路径是平滑的曲线

### 没有 GPX 数据时
- 不显示 GPX 标识
- 使用预定义的固定布局
- Breakpoint 按固定位置排列

## 常见问题

### Q: 地图显示为空
**A**: 检查：
1. 浏览器控制台是否有错误
2. GPX 数据格式是否正确
3. Breakpoint 是否有坐标

### Q: Breakpoint 位置不准确
**A**: 确保：
1. Breakpoint 的 `latitude` 和 `longitude` 字段有值
2. 坐标格式正确（数字，不是字符串）
3. GPX 轨迹覆盖了 breakpoint 所在区域

### Q: 路径显示不正确
**A**: 检查：
1. GPX 数据是否包含有效的 `<trkpt>` 元素
2. 坐标值是否在合理范围内（lat: -90 到 90, lon: -180 到 180）

## 性能考虑

- GPX 解析在客户端进行，使用 `useMemo` 缓存结果
- 大量轨迹点（>1000）可能需要优化投影算法
- 建议 GPX 数据不超过 10KB（压缩后）

