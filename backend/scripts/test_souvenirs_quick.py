#!/usr/bin/env python3
"""
快速测试脚本：测试Souvenir API基本功能（不等待AI生成）

这个脚本用于快速验证API是否正常工作，跳过AI生成步骤。
适用于：
- 快速验证API端点
- 测试数据流
- 调试API问题

使用方法:
    python scripts/test_souvenirs_quick.py [--profile-id PROFILE_ID] [--route-id ROUTE_ID]
"""
import httpx
import json
import sys
import argparse
from pathlib import Path

BASE_URL = "http://localhost:8000"
TIMEOUT = 30.0


def print_test(name: str):
    print(f"\n🔍 {name}...")


def print_success(msg: str):
    print(f"   ✅ {msg}")


def print_error(msg: str):
    print(f"   ❌ {msg}")


def print_info(msg: str):
    print(f"   ℹ️  {msg}")


def test_get_souvenirs(profile_id: int):
    """测试获取souvenirs列表"""
    print_test(f"获取Profile {profile_id}的Souvenirs列表")
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.get(
                f"{BASE_URL}/api/profiles/{profile_id}/souvenirs?limit=10"
            )
            if response.status_code == 200:
                data = response.json()
                souvenirs = data.get('souvenirs', [])
                total = data.get('total', 0)
                print_success(f"成功! Total: {total}, 返回: {len(souvenirs)}")
                if souvenirs:
                    print_info(f"最新souvenir: ID={souvenirs[0].get('id')}, "
                             f"XP={souvenirs[0].get('total_xp_gained')}")
                return True
            else:
                print_error(f"失败 (Status: {response.status_code})")
                print_error(response.text[:200])
                return False
    except Exception as e:
        print_error(f"错误: {e}")
        return False


def test_get_single_souvenir(profile_id: int, souvenir_id: int):
    """测试获取单个souvenir"""
    print_test(f"获取Souvenir {souvenir_id}")
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.get(
                f"{BASE_URL}/api/profiles/{profile_id}/souvenirs/{souvenir_id}"
            )
            if response.status_code == 200:
                souvenir = response.json()
                print_success(f"成功!")
                print_info(f"Route ID: {souvenir.get('route_id')}")
                print_info(f"XP Gained: {souvenir.get('total_xp_gained')}")
                print_info(f"Has AI Summary: {bool(souvenir.get('genai_summary'))}")
                return True
            else:
                print_error(f"失败 (Status: {response.status_code})")
                return False
    except Exception as e:
        print_error(f"错误: {e}")
        return False


def test_create_souvenir(profile_id: int, route_id: int, quest_ids: list[int] = None):
    """测试创建souvenir（快速模式，不等待AI）"""
    print_test(f"创建Souvenir (Route {route_id})")
    if quest_ids is None:
        quest_ids = []
    
    request_data = {
        "route_id": route_id,
        "completed_quest_ids": quest_ids
    }
    
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            print_info(f"请求数据: {json.dumps(request_data)}")
            response = client.post(
                f"{BASE_URL}/api/profiles/{profile_id}/souvenirs",
                json=request_data,
                timeout=TIMEOUT
            )
            if response.status_code == 200:
                data = response.json()
                souvenir_id = data.get('souvenir', {}).get('id')
                total_xp = data.get('total_xp_gained', 0)
                print_success(f"成功! Souvenir ID: {souvenir_id}, XP: {total_xp}")
                print_info(f"XP Breakdown: {json.dumps(data.get('xp_breakdown', {}), indent=2)}")
                return souvenir_id
            else:
                print_error(f"失败 (Status: {response.status_code})")
                print_error(response.text[:500])
                return None
    except httpx.TimeoutException:
        print_error("超时（AI生成可能需要更长时间）")
        return None
    except Exception as e:
        print_error(f"错误: {e}")
        return None


def test_sorting(profile_id: int):
    """测试排序功能"""
    print_test("测试排序功能")
    sorts = ["newest", "oldest", "xp_high", "xp_low"]
    
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            for sort in sorts:
                response = client.get(
                    f"{BASE_URL}/api/profiles/{profile_id}/souvenirs?sort={sort}&limit=3"
                )
                if response.status_code == 200:
                    data = response.json()
                    count = len(data.get('souvenirs', []))
                    print_info(f"{sort:10s}: {count} souvenirs")
                else:
                    print_error(f"{sort}: 失败 (Status: {response.status_code})")
        return True
    except Exception as e:
        print_error(f"错误: {e}")
        return False


def get_route_with_quests():
    """获取一个有quests的路线"""
    print_test("查找有Quests的路线")
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.get(
                f"{BASE_URL}/api/routes/recommendations?limit=20"
            )
            if response.status_code == 200:
                data = response.json()
                routes = data.get('routes', [])
                for route in routes:
                    breakpoints = route.get('breakpoints', [])
                    quest_ids = []
                    for bp in breakpoints:
                        quest_ids.extend([q.get('id') for q in bp.get('mini_quests', [])])
                    if quest_ids:
                        print_success(f"找到路线: {route.get('id')} - {route.get('title')}")
                        print_info(f"Quest IDs: {quest_ids[:5]}")
                        return {
                            'id': route.get('id'),
                            'quest_ids': quest_ids[:3]  # 只用前3个
                        }
                print_error("没有找到有quests的路线")
                return None
            else:
                print_error(f"获取路线失败 (Status: {response.status_code})")
                return None
    except Exception as e:
        print_error(f"错误: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description='快速测试Souvenir API')
    parser.add_argument('--profile-id', type=int, help='使用现有的profile ID')
    parser.add_argument('--route-id', type=int, help='使用指定的route ID')
    parser.add_argument('--souvenir-id', type=int, help='测试指定的souvenir ID')
    args = parser.parse_args()
    
    print("=" * 60)
    print("Souvenir API 快速测试")
    print("=" * 60)
    
    profile_id = args.profile_id
    
    # 如果没有提供profile_id，尝试创建一个
    if not profile_id:
        print_test("创建测试Profile")
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{BASE_URL}/api/profiles",
                    json={
                        "fitness": "intermediate",
                        "type": ["history-culture"],
                        "narrative": "adventure"
                    }
                )
                if response.status_code == 201:
                    profile_id = response.json().get('id')
                    print_success(f"Profile创建成功: ID={profile_id}")
                else:
                    print_error("无法创建Profile")
                    print_error(f"响应: {response.text[:200]}")
                    sys.exit(1)
        except Exception as e:
            print_error(f"创建Profile失败: {e}")
            sys.exit(1)
    
    # 测试获取souvenirs列表
    test_get_souvenirs(profile_id)
    
    # 如果提供了souvenir_id，测试获取单个souvenir
    if args.souvenir_id:
        test_get_single_souvenir(profile_id, args.souvenir_id)
    
    # 如果提供了route_id，测试创建souvenir
    if args.route_id:
        route = {'id': args.route_id, 'quest_ids': []}
    else:
        route = get_route_with_quests()
    
    if route:
        souvenir_id = test_create_souvenir(
            profile_id,
            route['id'],
            route.get('quest_ids', [])
        )
        
        if souvenir_id:
            # 等待一下
            import time
            time.sleep(1)
            
            # 测试获取刚创建的souvenir
            test_get_single_souvenir(profile_id, souvenir_id)
    
    # 测试排序
    test_sorting(profile_id)
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
    print(f"\n使用的Profile ID: {profile_id}")
    if route:
        print(f"使用的Route ID: {route['id']}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试被中断")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

