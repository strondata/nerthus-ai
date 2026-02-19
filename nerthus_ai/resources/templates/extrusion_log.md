# Relatório Técnico de Extrusão
**Contexto de Análise:** {{ collection_name }}
**Data do Relatório:** {{ report_date }}

## 1. Resumo dos Parâmetros de Processo
*(Compilado de {{ doc_count }} documentos encontrados)*

{{ llm_generated_process_summary }}

## 2. Análise de Materiais e Formulações
| Material Base | Aditivos | Observações de Performance |
| :--- | :--- | :--- |
{% for item in formulations %}
| {{ item.base }} | {{ item.additives }} | {{ item.performance_note }} |
{% endfor %}

## 3. Histórico de Problemas e Soluções
> **Anomalias Detectadas:**
> {{ anomalies_list }}

## 4. Conclusão Técnica
{{ conclusion_text }}
