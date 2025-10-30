# 专利交底书生成代理系统

## 使用：

```bash
# 配置环境变量
cp env.example env
cp .claude/settings.local.json.example .claude/settings.local.json

# 修改 .mcp.json 中的 API KEY，包括SERPAPI_API_KEY和EXA_API_KEY（或者在env中配置）
# 修改 .claude/settings.local.json 中的 Token 和 URL（配置为第三方模型，如果不使用第三方，删除掉以ANTHROPIC开头的env即可）

#CLI
source ./env
claude --dangerously-skip-permissions "根据 data/example_input.md 编写专利交底书 " -p  --output-format stream-json --verbose
```

## 工作流程图

```
输入材料 (Markdown)
    ↓
┌───────────────────────────────────────────────────────┐
│ 1. title-generator                                    │
│    输出：专利标题                                       │
└───────────────────────────────────────────────────────┘
    ↓
┌───────────────────────────────────────────────────────┐
│ 2. patent-searcher                                    │
│    输出：search-report.md（检索报告）                   │
│         similar-patents-reference.md（参考文件）       │
└───────────────────────────────────────────────────────┘
    ↓
┌───────────────────────────────────────────────────────┐
│ 3. purpose-writer                                     │
│    输入：原始材料 + 参考文件                            │
│    输出：purpose-section.md (1000-1500字)             │
└───────────────────────────────────────────────────────┘
    ↓
┌───────────────────────────────────────────────────────┐
│ 4. content-writer                                     │
│    输入：原始材料 + 参考文件 + purpose-section.md      │
│    输出：content-section.md (1500-2500字)             │
└───────────────────────────────────────────────────────┘
    ↓
┌───────────────────────────────────────────────────────┐
│ 5. diagram-generator                                  │
│    输入：content-section.md                           │
│    输出：diagrams.md (Mermaid 图表)                    │
└───────────────────────────────────────────────────────┘
    ↓
┌───────────────────────────────────────────────────────┐
│ 6. report-merger                                      │
│    输入：所有上述文件                                   │
│    输出：output.md (完整交底书, ≥3000字)                │
│    质量检查：术语统一、篇幅达标、逻辑一致               │
└───────────────────────────────────────────────────────┘
```
