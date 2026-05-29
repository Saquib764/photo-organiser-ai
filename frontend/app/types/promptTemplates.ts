export interface PromptTemplateSummary {
  id: string
  name: string
}

export interface PromptTemplateListResponse {
  templates: PromptTemplateSummary[]
}

export interface PromptTemplateContentResponse {
  id: string
  name: string
  content: string
}
