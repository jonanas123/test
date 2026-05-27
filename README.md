# Central Multimídia Automotiva 🚗

Software modular de infotainment automotivo com arquitetura em camadas,
simulando uma central multimídia moderna.

## Arquitetura

O sistema segue uma arquitetura em 3 camadas:

```
┌──────────────────────────────┐
│   HMI (Interface CLI)        │
├──────────────────────────────┤
│   Middleware (Lógica)        │
├──────────────────────────────┤
│   HAL (Abstração Hardware)   │
└──────────────────────────────┘
```

Documentação completa: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)

## Módulos

| Módulo           | Descrição                                         |
|------------------|---------------------------------------------------|
| **Boot**         | Tela de boas-vindas e verificação de subsistemas   |
| **Mídia**        | Play, Pause, Skip, Volume                         |
| **Climatização** | Controle de temperatura e ventilador (HVAC)        |
| **Conectividade**| Bluetooth e Wi-Fi (pareamento, conexão)            |
| **Veículo**      | Velocidade, combustível, alertas via CAN Bus       |

## Requisitos

- Python 3.10+

## Como Executar

```bash
# Clonar o repositório
git clone https://github.com/jonanas123/automotive-infotainment.git
cd automotive-infotainment

# Instalar dependências
pip install -r requirements.txt

# Executar a central multimídia
python main.py
```

## Como Testar

```bash
# Instalar dependências de teste
pip install pytest

# Executar testes
python -m pytest tests/ -v
```

## Estrutura do Projeto

```
automotive-infotainment/
├── docs/
│   └── ARCHITECTURE.md       # Documentação de arquitetura
├── src/
│   ├── hal/                  # Camada de Abstração de Hardware
│   │   ├── can_bus.py        # Interface CAN Bus
│   │   ├── bluetooth_hal.py  # Interface Bluetooth
│   │   ├── audio_hal.py      # Interface Áudio
│   │   ├── hvac_hal.py       # Interface Climatização
│   │   └── wifi_hal.py       # Interface Wi-Fi
│   ├── middleware/            # Camada de Lógica de Negócios
│   │   ├── boot_manager.py   # Gerenciador de Boot
│   │   ├── connectivity_manager.py  # Gerenciador de Conectividade
│   │   ├── media_manager.py  # Gerenciador de Mídia
│   │   ├── hvac_manager.py   # Gerenciador de Climatização
│   │   └── vehicle_manager.py # Gerenciador Veicular
│   └── hmi/                  # Camada de Interface
│       ├── display.py        # Renderização de tela
│       └── input_handler.py  # Captura de entrada
├── tests/                    # Testes unitários
├── main.py                   # Ponto de entrada
├── requirements.txt
└── README.md
```

## Princípios de Design

- **SOLID**: Cada módulo tem responsabilidade única, depende de abstrações
- **Injeção de dependência**: HAL é injetada nos Managers via construtor
- **Mock-first**: Hardware simulado para desenvolvimento sem hardware real
- **Modularidade**: Novos módulos podem ser adicionados sem alterar os existentes
