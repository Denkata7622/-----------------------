// data/config.js — AI конфигурация за client-side функции
// ВНИМАНИЕ: API ключът се вижда от потребителя. ОК за локален сайт.

window.AI_CONFIG = {
  models: [
    { id: 'z-ai/glm-5.3-flash',         label: 'GLM 5.3 Flash' },
    { id: 'deepseek/deepseek-v3.2',     label: 'DeepSeek V3.2' },
    { id: 'openai/gpt-oss-120b',        label: 'gpt-oss-120b' },
    { id: 'openai/gpt-6.1-sol',         label: 'GPT-6.1 Sol' },
    { id: 'openai/gpt-6.1-sol-pro',     label: 'GPT-6.1 Sol Pro' },
  ],
  api_url: "/api/chat",           // ← relative, same-origin
  api_key: "",
  model: "z-ai/glm-5.3-flash",           // ← за тестване, $0.0006/чат
  memory_model: "z-ai/glm-5.3-flash"     // ← за тестване, $0.0006/extract
};