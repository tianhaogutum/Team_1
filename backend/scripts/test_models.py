# backend/scripts/test_models.py
"""
简单的测试脚本，验证 data models 是否正确工作。
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db, init_db
from app.models.entities import (
    Breakpoint,
    DemoProfile,
    MiniQuest,
    Route,
    Souvenir,
)
from app.settings import get_settings


async def test_models() -> None:
    """测试所有模型的基本功能。"""
    print("🧪 开始测试 Data Models...\n")
    
    settings = get_settings()
    init_db(settings)
    
    async with get_db() as session:
        # 测试 1: 创建 Route
        print("1️⃣ 测试创建 Route...")
        route = Route(
            id=9999,
            title="Test Route",
            category_name="hikingTourTrail",
            length_meters=5000.0,
            duration_min=60,
            difficulty=2,
            short_description="A test route for model validation",
            xp_required=0,
        )
        session.add(route)
        await session.flush()
        print(f"   ✅ Route 创建成功: {route}")
        
        # 测试 2: 创建 Breakpoint
        print("\n2️⃣ 测试创建 Breakpoint...")
        breakpoint = Breakpoint(
            route_id=route.id,
            order_index=0,
            poi_name="Test POI",
            poi_type="landmark",
            latitude=47.7989,
            longitude=13.0436,
            main_quest_snippet="Test quest snippet",
        )
        session.add(breakpoint)
        await session.flush()
        print(f"   ✅ Breakpoint 创建成功: {breakpoint}")
        
        # 测试 3: 创建 MiniQuest
        print("\n3️⃣ 测试创建 MiniQuest...")
        mini_quest = MiniQuest(
            breakpoint_id=breakpoint.id,
            task_description="Test task: take a photo",
            xp_reward=20,
        )
        session.add(mini_quest)
        await session.flush()
        print(f"   ✅ MiniQuest 创建成功: {mini_quest}")
        
        # 测试 4: 创建 DemoProfile
        print("\n4️⃣ 测试创建 DemoProfile...")
        profile = DemoProfile(
            total_xp=100,
            level=2,
            user_vector_json='{"fitness": 3, "preference": "hiking"}',
            genai_welcome_summary="Test welcome message",
        )
        session.add(profile)
        await session.flush()
        print(f"   ✅ DemoProfile 创建成功: {profile}")
        
        # 测试 5: 创建 Souvenir
        print("\n5️⃣ 测试创建 Souvenir...")
        souvenir = Souvenir(
            demo_profile_id=profile.id,
            route_id=route.id,
            total_xp_gained=150,
            genai_summary="Test completion summary",
            xp_breakdown_json='{"base": 100, "quests": 50}',
        )
        session.add(souvenir)
        await session.flush()
        print(f"   ✅ Souvenir 创建成功: {souvenir}")
        
        # 测试 6: 测试关系 (Relationships)
        print("\n6️⃣ 测试模型关系...")
        
        # 测试 Route -> Breakpoints (使用 selectinload 预先加载关系)
        result = await session.execute(
            select(Route)
            .where(Route.id == route.id)
            .options(selectinload(Route.breakpoints))
        )
        loaded_route = result.scalar_one()
        print(f"   Route.breakpoints: {len(loaded_route.breakpoints)} 个 breakpoints")
        assert len(loaded_route.breakpoints) == 1, "Route 应该有 1 个 breakpoint"
        print("   ✅ Route -> Breakpoints 关系正常")
        
        # 测试 Breakpoint -> MiniQuests (使用 selectinload 预先加载关系)
        result = await session.execute(
            select(Breakpoint)
            .where(Breakpoint.id == breakpoint.id)
            .options(selectinload(Breakpoint.mini_quests))
        )
        loaded_breakpoint = result.scalar_one()
        print(f"   Breakpoint.mini_quests: {len(loaded_breakpoint.mini_quests)} 个 mini-quests")
        assert len(loaded_breakpoint.mini_quests) == 1, "Breakpoint 应该有 1 个 mini-quest"
        print("   ✅ Breakpoint -> MiniQuests 关系正常")
        
        # 测试 DemoProfile -> Souvenirs (使用 selectinload 预先加载关系)
        result = await session.execute(
            select(DemoProfile)
            .where(DemoProfile.id == profile.id)
            .options(selectinload(DemoProfile.souvenirs))
        )
        loaded_profile = result.scalar_one()
        print(f"   DemoProfile.souvenirs: {len(loaded_profile.souvenirs)} 个 souvenirs")
        assert len(loaded_profile.souvenirs) == 1, "Profile 应该有 1 个 souvenir"
        print("   ✅ DemoProfile -> Souvenirs 关系正常")
        
        # 测试 7: 查询测试
        print("\n7️⃣ 测试查询功能...")
        
        # 查询所有 routes
        result = await session.execute(select(Route))
        all_routes = result.scalars().all()
        print(f"   查询到 {len(all_routes)} 个 routes")
        assert len(all_routes) > 0, "应该至少有一个 route"
        print("   ✅ 查询功能正常")
        
        # 测试 8: 测试级联删除 (Cascade Delete)
        print("\n8️⃣ 测试级联删除...")
        await session.delete(route)  # 删除 route 应该级联删除 breakpoint 和 mini_quest
        await session.flush()
        
        # 验证 breakpoint 也被删除
        result = await session.execute(
            select(Breakpoint).where(Breakpoint.id == breakpoint.id)
        )
        deleted_breakpoint = result.scalar_one_or_none()
        assert deleted_breakpoint is None, "Breakpoint 应该被级联删除"
        print("   ✅ 级联删除功能正常")
        
        # 清理测试数据
        await session.delete(profile)  # 这会级联删除 souvenir
        # get_db() 会在退出上下文时自动 commit，所以不需要手动 commit
        
        print("\n" + "="*50)
        print("🎉 所有测试通过！Data Models 工作正常！")
        print("="*50)


if __name__ == "__main__":
    try:
        asyncio.run(test_models())
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)