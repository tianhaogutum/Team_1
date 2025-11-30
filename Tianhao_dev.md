# Remaining Features to be Implemented

## 🔴 High Priority

### AI Storytelling System
- **Status**: API implemented but has unacceptable latency
- **Task**: Batch generate mock breakpoints data, then pre-generate:
  - Prologue for each route
  - Epilogue for each route
  - Story snippets for each breakpoint
- **Action**: Store pre-generated content in DB for fast FE display

### Feedback Loop (US-08)
- **Status**: Negative feedback API not implemented
- **Backend**: Missing API endpoint for negative feedback
- **Frontend**: Button exists but not calling any API
---

## 🟡 Medium Priority

### Souvenir System
- **Backend**: 
  - Generation rules & DB schema/logic only partly thought through
- **Frontend**: 
  - Gallery page missing
  - Spotlight component missing
  - Wiring/connections still missing

### Gamification Logic 1号，实现lock的逻辑
- **Route Locking/Unlocking**: 
  - Currently only mocked on FE
  - Need real XP-based locking logic
- **Achievements**: 
  - Currently mock data only
  - Need real rules and storage

---

## 🟢 Low Priority

### Side Quests / Quizzes
- **Backend**: 
  - No BE model yet
  - No GenAI logic yet
- **Frontend**: 
  - Only has placeholder UI

### Breakpoint Map Logic
- **Status**: FE visual is there
- **Backend**: 
  - Breakpoint coordinates may not be fully defined in DB
  - Breakpoint order in DB + API may not be fully defined

---

## Notes
- Prioritize features based on user impact and technical complexity
- Consider batch processing for AI-generated content to improve performance
- Ensure FE and BE are properly wired before marking features as complete

暂定实现，未来实现的功能：
1. 登陆功能，数据的持久化