# OrbitGuard

Dashboard de monitoramento de status orbital e risco de colisao com detritos espaciais,
publicado no Azure App Service com pipeline CI/CD (GitHub Actions), Azure Key Vault e
Application Insights.

## Conexao com a Industria Espacial e ODS
- **Problema:** a orbita baixa da Terra (LEO) acumula milhares de detritos que ameacam
  satelites ativos e missoes, com risco de colisoes em cascata (sindrome de Kessler).
- **Solucao:** o OrbitGuard consome dados orbitais reais, calcula altitude/velocidade/risco
  e apoia hipoteticamente a deteccao e a coleta de detritos.
- **ODS prioritario:** ODS 9 - Industria, Inovacao e Infraestrutura.

## Fonte de dados (real)
- API publica **CelesTrak** (GP/TLE), grupo `cosmos-2251-debris` (fragmentos reais da
  colisao Cosmos-2251 / Iridium-33 de 2009). Sem necessidade de login ou chave.
- Altitude e velocidade calculadas a partir dos elementos orbitais (3a lei de Kepler).
- Cache de 2h + fallback automatico para dados simulados caso a API esteja indisponivel.

## Arquitetura
- **App Service** (Python 3.11 / Flask + gunicorn), HTTPS-only.
- **Application Insights** para monitoramento e alertas.
- **Key Vault** para segredos da solucao.
- **GitHub Actions**: push na branch `main` -> deploy automatico no App Service.

## Endpoints
- `/` - dashboard
- `/api/objects` - JSON com objetos e resumo de risco
- `/health` - healthcheck

## Equipe
- Joao Victor dos Santos Morais - RM550453
- Pedro Henrique Farath - RM98608
- Juliana Maita - RM99224
- Luana Cabezaolias - RM99320
- Luca Vilaca - RM551538
