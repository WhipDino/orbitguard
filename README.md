# OrbitGuard

**Dashboard de Status Orbital e Risco de Colisao** | Global Solution / SDTCC - Industria Espacial

## Identidade do produto
- **Nome:** OrbitGuard
- **Proposito:** Monitorar objetos em orbita (satelites ativos e detritos espaciais), estimar
  o risco de colisao em tempo quase real e apoiar decisoes de manobra evasiva, contribuindo
  para a sustentabilidade do ambiente orbital.
- **Equipe:** [INTEGRANTE 1 - RM], [INTEGRANTE 2 - RM], [INTEGRANTE 3 - RM]

## Problema espacial e ODS
A quantidade crescente de detritos espaciais ameaca satelites operacionais e missoes futuras
(sindrome de Kessler). O OrbitGuard detecta e prioriza objetos por probabilidade de colisao.
**ODS 9 - Industria, Inovacao e Infraestrutura** (infraestrutura espacial resiliente).

## Arquitetura (Azure)
- **App Service** (Linux, Python 3.11) hospeda o dashboard Flask - URL publica HTTPS.
- **Application Insights** para monitoramento e alertas.
- **Key Vault** para guarda de segredos (connection string).
- **GitHub Actions** para CI/CD (deploy automatico no push para main).

## Rotas
- `/` dashboard (HTML)
- `/api/objects` dados simulados (JSON)
- `/health` healthcheck

## Rodar localmente
```
pip install -r requirements.txt
python app.py
```
