# Arquitetura do Sistema de Infotainment Automotivo

## Visão Geral

O sistema de infotainment segue uma **arquitetura em camadas (Layered Architecture)** inspirada
nos padrões da indústria automotiva (AUTOSAR Adaptive, Android Automotive).
Cada camada possui responsabilidades bem definidas e se comunica apenas com as
camadas adjacentes, promovendo baixo acoplamento e alta coesão.

```
┌─────────────────────────────────────────────────┐
│              CAMADA DE INTERFACE (HMI)           │
│  Console CLI  │  (Futuramente: Qt/Flutter GUI)   │
├─────────────────────────────────────────────────┤
│         CAMADA DE LÓGICA DE NEGÓCIOS             │
│          (MIDDLEWARE / SERVIÇOS)                  │
│  ┌──────────┐ ┌────────────┐ ┌───────────────┐  │
│  │   Boot   │ │Conectividade│ │    Mídia      │  │
│  └──────────┘ └────────────┘ └───────────────┘  │
│  ┌──────────────┐ ┌─────────────────────────┐   │
│  │  Climatização│ │  Integração Veicular    │   │
│  │    (HVAC)    │ │     (Rede CAN)          │   │
│  └──────────────┘ └─────────────────────────┘   │
├─────────────────────────────────────────────────┤
│     CAMADA DE ABSTRAÇÃO DE HARDWARE (HAL)        │
│  CAN Bus Driver │ Bluetooth HAL │ Audio HAL      │
│  HVAC HAL       │ Display HAL   │ Wi-Fi HAL      │
└─────────────────────────────────────────────────┘
         ▼               ▼              ▼
   ┌──────────┐   ┌──────────┐   ┌──────────┐
   │ Hardware │   │ Hardware │   │ Hardware │
   │  CAN Bus │   │Bluetooth │   │  Áudio   │
   └──────────┘   └──────────┘   └──────────┘
```

---

## Camadas do Sistema

### 1. Camada de Abstração de Hardware (HAL)

**Responsabilidade:** Isolar o software da complexidade do hardware real.
Fornece interfaces abstratas (ABCs em Python) que podem ser implementadas
por drivers reais ou mocks para simulação.

**Módulos:**
- `can_bus.py` — Interface e mock para comunicação com a rede CAN do veículo
- `bluetooth_hal.py` — Abstração de pareamento e conexão Bluetooth
- `audio_hal.py` — Abstração de saída de áudio (volume, roteamento)
- `hvac_hal.py` — Abstração de sensores e atuadores de climatização
- `wifi_hal.py` — Abstração do módulo Wi-Fi

**Princípios aplicados:**
- **Dependency Inversion (DIP):** O middleware depende de abstrações (ABCs),
  não de implementações concretas de hardware.
- **Interface Segregation (ISP):** Cada HAL expõe apenas os métodos relevantes
  ao seu domínio.

### 2. Camada de Lógica de Negócios (Middleware)

**Responsabilidade:** Orquestrar os fluxos do sistema. Contém toda a lógica
de negócios, processamento de dados e gerenciamento de estado.

**Módulos:**
- `boot_manager.py` — Inicialização do sistema, verificação de subsistemas,
  tela de boas-vindas.
- `connectivity_manager.py` — Gerenciamento de Bluetooth e Wi-Fi
  (pareamento, status, desconexão).
- `media_manager.py` — Controle do player de mídia (play, pause, skip,
  volume).
- `hvac_manager.py` — Controle de temperatura e velocidade do ventilador
  com limites de segurança.
- `vehicle_manager.py` — Leitura e processamento de dados veiculares
  via CAN Bus (velocidade, combustível, alertas).

**Princípios aplicados:**
- **Single Responsibility (SRP):** Cada manager é responsável por um
  único domínio funcional.
- **Open/Closed (OCP):** Novos módulos podem ser adicionados sem alterar
  os existentes.

### 3. Camada de Interface (HMI)

**Responsabilidade:** Apresentar informações ao usuário e capturar entradas.
Nesta versão, implementada como uma interface CLI interativa. A arquitetura
permite substituir por uma GUI (Qt, Flutter, Web) sem alterar middleware ou HAL.

**Módulos:**
- `display.py` — Renderização da interface no terminal (menus, painéis,
  status em tempo real).
- `input_handler.py` — Captura e roteamento de entradas do usuário.

**Princípios aplicados:**
- **Liskov Substitution (LSP):** Qualquer implementação de HMI (CLI, GUI)
  pode ser usada de forma intercambiável desde que respeite a interface.

---

## Fluxo de Comunicação

```
Usuário ─► HMI (CLI) ─► Middleware (Managers) ─► HAL (Abstrações) ─► Hardware (Mock)
                              │
                              ▼
                        Estado do Sistema
                        (em memória)
```

1. O usuário interage via menus CLI
2. O `InputHandler` roteia a ação ao Manager correto
3. O Manager processa a lógica e chama o HAL correspondente
4. O HAL executa a operação (simulada via mock/log)
5. O estado atualizado é refletido no display

---

## Tecnologias

| Componente        | Tecnologia                      |
|-------------------|----------------------------------|
| Linguagem         | Python 3.10+                     |
| Arquitetura       | Layered (3-Tier)                 |
| Abstrações        | ABC (Abstract Base Classes)      |
| Simulação HW      | Mock implementations com logging |
| Interface          | CLI interativa (curses-free)     |
| Testes             | pytest                           |

---

## Estrutura de Diretórios

```
automotive-infotainment/
├── docs/
│   └── ARCHITECTURE.md          # Este documento
├── src/
│   ├── __init__.py
│   ├── hal/                     # Camada de Abstração de Hardware
│   │   ├── __init__.py
│   │   ├── can_bus.py
│   │   ├── bluetooth_hal.py
│   │   ├── audio_hal.py
│   │   ├── hvac_hal.py
│   │   └── wifi_hal.py
│   ├── middleware/               # Camada de Lógica de Negócios
│   │   ├── __init__.py
│   │   ├── boot_manager.py
│   │   ├── connectivity_manager.py
│   │   ├── media_manager.py
│   │   ├── hvac_manager.py
│   │   └── vehicle_manager.py
│   └── hmi/                     # Camada de Interface
│       ├── __init__.py
│       ├── display.py
│       └── input_handler.py
├── tests/
│   ├── __init__.py
│   ├── test_boot.py
│   ├── test_media.py
│   ├── test_hvac.py
│   ├── test_connectivity.py
│   └── test_vehicle.py
├── main.py                      # Ponto de entrada do sistema
├── requirements.txt
└── README.md
```

---

## Decisões de Design

1. **Mock-first approach:** Todo o hardware é simulado via classes mock que
   implementam as ABCs da HAL. Isso permite desenvolvimento e teste sem
   hardware real.

2. **Injeção de dependência:** Os managers recebem suas dependências HAL
   via construtor, facilitando testes unitários e troca de implementações.

3. **Estado centralizado por módulo:** Cada manager mantém seu próprio
   estado interno, evitando estado global compartilhado.

4. **Logging estruturado:** Todas as operações HAL geram logs que simulam
   a comunicação com hardware real, facilitando debugging e auditoria.
