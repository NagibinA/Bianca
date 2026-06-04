/**
 * BIANCA SIMPLE DASHBOARD STRATEGY
 * Version: 1.0.0
 * Упрощённая панель управления с кнопками-чипсами и плитками опций
 */

class BiancaSimpleDashboardStrategy extends HTMLElement {
    static getCreateSuggestions(_hass) {
        return {
            title: "Bianca Simple",
            icon: "mdi:washing-machine",
        };
    }

    static async generate(config, hass, resources, view) {
        return {
            title: "Bianca Simple",
            views: [
                {
                    title: "Управление",
                    type: "sections",
                    sections: [
                        {
                            type: "grid",
                            cards: [
                                {
                                    type: "custom:button-card",
                                    template: "card_modern",
                                    name: "Bianca",
                                    icon: "mdi:washing-machine",
                                    show_state: true,
                                    entity: "binary_sensor.bianca_available",
                                    state_display: [
                                        {
                                            operator: "default",
                                            value: "offline",
                                            name: "Офлайн",
                                            color: "grey"
                                        },
                                        {
                                            operator: "default",
                                            value: "online",
                                            name: "Онлайн",
                                            color: "green"
                                        }
                                    ],
                                    styles: {
                                        card: [
                                            {
                                                "background-color": "var(--card-background-color)"
                                            }
                                        ]
                                    }
                                },
                                {
                                    type: "grid",
                                    columns: 2,
                                    cards: [
                                        {
                                            type: "custom:button-card",
                                            color_type: "icon",
                                            color: "green",
                                            name: "СТАРТ",
                                            icon: "mdi:play-circle",
                                            size: "40px",
                                            tap_action: {
                                                action: "perform-action",
                                                perform_action: "bianca.start_washing"
                                            },
                                            styles: {
                                                card: [
                                                    {
                                                        "background-color": "rgba(76, 175, 80, 0.1)",
                                                        "border-radius": "12px",
                                                        "padding": "16px"
                                                    }
                                                ],
                                                name: [
                                                    {
                                                        "color": "#4CAF50",
                                                        "font-weight": "bold"
                                                    }
                                                ]
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if is_state('binary_sensor.bianca_available', 'on') and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                        opacity: 1;
                                                        pointer-events: auto;
                                                        {% else %}
                                                        opacity: 0.5;
                                                        pointer-events: none;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            type: "custom:button-card",
                                            color_type: "icon",
                                            color: "red",
                                            name: "СТОП",
                                            icon: "mdi:stop-circle",
                                            size: "40px",
                                            tap_action: {
                                                action: "perform-action",
                                                perform_action: "bianca.stop_washing"
                                            },
                                            styles: {
                                                card: [
                                                    {
                                                        "background-color": "rgba(244, 67, 54, 0.1)",
                                                        "border-radius": "12px",
                                                        "padding": "16px"
                                                    }
                                                ],
                                                name: [
                                                    {
                                                        "color": "#F44336",
                                                        "font-weight": "bold"
                                                    }
                                                ]
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if is_state('binary_sensor.bianca_available', 'on') and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') %}
                                                            {% if not machine_ready %}
                                                            opacity: 1;
                                                            pointer-events: auto;
                                                            {% else %}
                                                            opacity: 0.5;
                                                            pointer-events: none;
                                                            {% endif %}
                                                        {% else %}
                                                        opacity: 0.5;
                                                        pointer-events: none;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        }
                                    ]
                                },
                                {
                                    type: "entities",
                                    title: "📋 ПРОГРАММА",
                                    show_header_toggle: false,
                                    entities: [
                                        {
                                            entity: "select.bianca_program",
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if not is_state('binary_sensor.bianca_available', 'on') %}
                                                        display: none;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        }
                                    ]
                                },
                                {
                                    type: "grid",
                                    columns: 1,
                                    cards: [
                                        {
                                            type: "horizontal-stack",
                                            cards: [
                                                {
                                                    type: "custom:button-card",
                                                    name: "ОСТАЛОСЬ",
                                                    icon: "mdi:timer-outline",
                                                    show_state: true,
                                                    entity: "sensor.bianca_remaining_time",
                                                    styles: {
                                                        card: [
                                                            {
                                                                "border-radius": "12px",
                                                                "padding": "12px"
                                                            }
                                                        ],
                                                        name: [
                                                            {
                                                                "font-size": "12px",
                                                                "color": "var(--secondary-text-color)"
                                                            }
                                                        ]
                                                    },
                                                    card_mod: {
                                                        style: `
                                                            :host {
                                                                {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                                    {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                                    {% if machine_ready %}
                                                                    display: none;
                                                                    {% endif %}
                                                                {% else %}
                                                                display: none;
                                                                {% endif %}
                                                            }
                                                        `
                                                    }
                                                },
                                                {
                                                    type: "custom:button-card",
                                                    name: "ФАЗА",
                                                    icon: "mdi:progress-clock",
                                                    show_state: true,
                                                    entity: "sensor.bianca_program_phase",
                                                    styles: {
                                                        card: [
                                                            {
                                                                "border-radius": "12px",
                                                                "padding": "12px"
                                                            }
                                                        ],
                                                        name: [
                                                            {
                                                                "font-size": "12px",
                                                                "color": "var(--secondary-text-color)"
                                                            }
                                                        ]
                                                    },
                                                    card_mod: {
                                                        style: `
                                                            :host {
                                                                {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                                    {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                                    {% if machine_ready %}
                                                                    display: none;
                                                                    {% endif %}
                                                                {% else %}
                                                                display: none;
                                                                {% endif %}
                                                            }
                                                        `
                                                    }
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    type: "entities",
                                    title: "⚙️ ОПЦИИ",
                                    show_header_toggle: false,
                                    entities: []
                                },
                                {
                                    type: "grid",
                                    columns: 3,
                                    cards: [
                                        {
                                            type: "custom:button-card",
                                            entity: "select.bianca_temperature",
                                            name: "🌡️",
                                            show_state: true,
                                            tap_action: {
                                                action: "perform-action",
                                                perform_action: "select.select_next",
                                                target: { entity_id: "select.bianca_temperature" },
                                                data: { cycle: true }
                                            },
                                            styles: {
                                                card: [
                                                    {
                                                        "border-radius": "12px",
                                                        "padding": "8px",
                                                        "text-align": "center"
                                                    }
                                                ],
                                                state: [
                                                    {
                                                        "font-size": "14px",
                                                        "font-weight": "bold"
                                                    }
                                                ]
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% if not machine_ready %}
                                                            opacity: 0.5;
                                                            pointer-events: none;
                                                            {% endif %}
                                                        {% else %}
                                                        opacity: 0.3;
                                                        pointer-events: none;
                                                        {% endif %}
                                                    }
                                                    ha-card {
                                                        background: var(--card-background-color);
                                                        border: 1px solid var(--divider-color);
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            type: "custom:button-card",
                                            entity: "select.bianca_spin",
                                            name: "🔄",
                                            show_state: true,
                                            tap_action: {
                                                action: "perform-action",
                                                perform_action: "select.select_next",
                                                target: { entity_id: "select.bianca_spin" },
                                                data: { cycle: true }
                                            },
                                            styles: {
                                                card: [
                                                    {
                                                        "border-radius": "12px",
                                                        "padding": "8px",
                                                        "text-align": "center"
                                                    }
                                                ],
                                                state: [
                                                    {
                                                        "font-size": "14px",
                                                        "font-weight": "bold"
                                                    }
                                                ]
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% if not machine_ready %}
                                                            opacity: 0.5;
                                                            pointer-events: none;
                                                            {% endif %}
                                                        {% else %}
                                                        opacity: 0.3;
                                                        pointer-events: none;
                                                        {% endif %}
                                                    }
                                                    ha-card {
                                                        background: var(--card-background-color);
                                                        border: 1px solid var(--divider-color);
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            type: "custom:button-card",
                                            entity: "select.bianca_soil",
                                            name: "💧",
                                            show_state: true,
                                            tap_action: {
                                                action: "perform-action",
                                                perform_action: "select.select_next",
                                                target: { entity_id: "select.bianca_soil" },
                                                data: { cycle: true }
                                            },
                                            styles: {
                                                card: [
                                                    {
                                                        "border-radius": "12px",
                                                        "padding": "8px",
                                                        "text-align": "center"
                                                    }
                                                ],
                                                state: [
                                                    {
                                                        "font-size": "14px",
                                                        "font-weight": "bold"
                                                    }
                                                ]
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% if not machine_ready %}
                                                            opacity: 0.5;
                                                            pointer-events: none;
                                                            {% endif %}
                                                        {% else %}
                                                        opacity: 0.3;
                                                        pointer-events: none;
                                                        {% endif %}
                                                    }
                                                    ha-card {
                                                        background: var(--card-background-color);
                                                        border: 1px solid var(--divider-color);
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            type: "custom:button-card",
                                            entity: "select.bianca_steam",
                                            name: "💨",
                                            show_state: true,
                                            tap_action: {
                                                action: "perform-action",
                                                perform_action: "select.select_next",
                                                target: { entity_id: "select.bianca_steam" },
                                                data: { cycle: true }
                                            },
                                            styles: {
                                                card: [
                                                    {
                                                        "border-radius": "12px",
                                                        "padding": "8px",
                                                        "text-align": "center"
                                                    }
                                                ],
                                                state: [
                                                    {
                                                        "font-size": "14px",
                                                        "font-weight": "bold"
                                                    }
                                                ]
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% if not machine_ready %}
                                                            opacity: 0.5;
                                                            pointer-events: none;
                                                            {% endif %}
                                                        {% else %}
                                                        opacity: 0.3;
                                                        pointer-events: none;
                                                        {% endif %}
                                                    }
                                                    ha-card {
                                                        background: var(--card-background-color);
                                                        border: 1px solid var(--divider-color);
                                                    }
                                                `
                                            }
                                        }
                                    ]
                                },
                                {
                                    type: "grid",
                                    columns: 4,
                                    cards: [
                                        {
                                            type: "custom:button-card",
                                            entity: "select.bianca_pre_wash",
                                            name: "🧼",
                                            show_state: true,
                                            tap_action: {
                                                action: "perform-action",
                                                perform_action: "select.select_next",
                                                target: { entity_id: "select.bianca_pre_wash" },
                                                data: { cycle: true }
                                            },
                                            styles: {
                                                card: [
                                                    {
                                                        "border-radius": "12px",
                                                        "padding": "8px",
                                                        "text-align": "center"
                                                    }
                                                ],
                                                state: [
                                                    {
                                                        "font-size": "11px",
                                                        "font-weight": "bold"
                                                    }
                                                ],
                                                name: [
                                                    {
                                                        "font-size": "16px"
                                                    }
                                                ]
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% set has_prewash = 'Есть' in state_attr('select.bianca_pre_wash', 'options') %}
                                                            {% if not machine_ready or not has_prewash %}
                                                            opacity: 0.5;
                                                            pointer-events: none;
                                                            {% endif %}
                                                            {% set prewash_val = states('select.bianca_pre_wash') %}
                                                            {% if prewash_val == 'Есть' %}
                                                            ha-card {
                                                                background: rgba(76, 175, 80, 0.2);
                                                                border-color: #4CAF50;
                                                            }
                                                            {% endif %}
                                                        {% else %}
                                                        opacity: 0.3;
                                                        pointer-events: none;
                                                        {% endif %}
                                                    }
                                                    ha-card {
                                                        background: var(--card-background-color);
                                                        border: 1px solid var(--divider-color);
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            type: "custom:button-card",
                                            entity: "select.bianca_hygiene",
                                            name: "🦠",
                                            show_state: true,
                                            tap_action: {
                                                action: "perform-action",
                                                perform_action: "select.select_next",
                                                target: { entity_id: "select.bianca_hygiene" },
                                                data: { cycle: true }
                                            },
                                            styles: {
                                                card: [
                                                    {
                                                        "border-radius": "12px",
                                                        "padding": "8px",
                                                        "text-align": "center"
                                                    }
                                                ],
                                                state: [
                                                    {
                                                        "font-size": "11px",
                                                        "font-weight": "bold"
                                                    }
                                                ],
                                                name: [
                                                    {
                                                        "font-size": "16px"
                                                    }
                                                ]
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% set has_hygiene = 'Есть' in state_attr('select.bianca_hygiene', 'options') %}
                                                            {% if not machine_ready or not has_hygiene %}
                                                            opacity: 0.5;
                                                            pointer-events: none;
                                                            {% endif %}
                                                            {% set hygiene_val = states('select.bianca_hygiene') %}
                                                            {% if hygiene_val == 'Есть' %}
                                                            ha-card {
                                                                background: rgba(76, 175, 80, 0.2);
                                                                border-color: #4CAF50;
                                                            }
                                                            {% endif %}
                                                        {% else %}
                                                        opacity: 0.3;
                                                        pointer-events: none;
                                                        {% endif %}
                                                    }
                                                    ha-card {
                                                        background: var(--card-background-color);
                                                        border: 1px solid var(--divider-color);
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            type: "custom:button-card",
                                            entity: "select.bianca_anti_crease",
                                            name: "↩️",
                                            show_state: true,
                                            tap_action: {
                                                action: "perform-action",
                                                perform_action: "select.select_next",
                                                target: { entity_id: "select.bianca_anti_crease" },
                                                data: { cycle: true }
                                            },
                                            styles: {
                                                card: [
                                                    {
                                                        "border-radius": "12px",
                                                        "padding": "8px",
                                                        "text-align": "center"
                                                    }
                                                ],
                                                state: [
                                                    {
                                                        "font-size": "11px",
                                                        "font-weight": "bold"
                                                    }
                                                ],
                                                name: [
                                                    {
                                                        "font-size": "16px"
                                                    }
                                                ]
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% set has_anticrease = 'Есть' in state_attr('select.bianca_anti_crease', 'options') %}
                                                            {% if not machine_ready or not has_anticrease %}
                                                            opacity: 0.5;
                                                            pointer-events: none;
                                                            {% endif %}
                                                            {% set anticrease_val = states('select.bianca_anti_crease') %}
                                                            {% if anticrease_val == 'Есть' %}
                                                            ha-card {
                                                                background: rgba(76, 175, 80, 0.2);
                                                                border-color: #4CAF50;
                                                            }
                                                            {% endif %}
                                                        {% else %}
                                                        opacity: 0.3;
                                                        pointer-events: none;
                                                        {% endif %}
                                                    }
                                                    ha-card {
                                                        background: var(--card-background-color);
                                                        border: 1px solid var(--divider-color);
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            type: "custom:button-card",
                                            entity: "select.bianca_night_spin",
                                            name: "🌙",
                                            show_state: true,
                                            tap_action: {
                                                action: "perform-action",
                                                perform_action: "select.select_next",
                                                target: { entity_id: "select.bianca_night_spin" },
                                                data: { cycle: true }
                                            },
                                            styles: {
                                                card: [
                                                    {
                                                        "border-radius": "12px",
                                                        "padding": "8px",
                                                        "text-align": "center"
                                                    }
                                                ],
                                                state: [
                                                    {
                                                        "font-size": "11px",
                                                        "font-weight": "bold"
                                                    }
                                                ],
                                                name: [
                                                    {
                                                        "font-size": "16px"
                                                    }
                                                ]
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% set has_nightspin = 'Есть' in state_attr('select.bianca_night_spin', 'options') %}
                                                            {% if not machine_ready or not has_nightspin %}
                                                            opacity: 0.5;
                                                            pointer-events: none;
                                                            {% endif %}
                                                            {% set nightspin_val = states('select.bianca_night_spin') %}
                                                            {% if nightspin_val == 'Есть' %}
                                                            ha-card {
                                                                background: rgba(76, 175, 80, 0.2);
                                                                border-color: #4CAF50;
                                                            }
                                                            {% endif %}
                                                        {% else %}
                                                        opacity: 0.3;
                                                        pointer-events: none;
                                                        {% endif %}
                                                    }
                                                    ha-card {
                                                        background: var(--card-background-color);
                                                        border: 1px solid var(--divider-color);
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            type: "custom:button-card",
                                            entity: "select.bianca_extra_rinse",
                                            name: "💦",
                                            show_state: true,
                                            tap_action: {
                                                action: "perform-action",
                                                perform_action: "select.select_next",
                                                target: { entity_id: "select.bianca_extra_rinse" },
                                                data: { cycle: true }
                                            },
                                            styles: {
                                                card: [
                                                    {
                                                        "border-radius": "12px",
                                                        "padding": "8px",
                                                        "text-align": "center"
                                                    }
                                                ],
                                                state: [
                                                    {
                                                        "font-size": "11px",
                                                        "font-weight": "bold"
                                                    }
                                                ],
                                                name: [
                                                    {
                                                        "font-size": "16px"
                                                    }
                                                ]
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% set has_rinse = '1 полоскание' in state_attr('select.bianca_extra_rinse', 'options') %}
                                                            {% if not machine_ready or not has_rinse %}
                                                            opacity: 0.5;
                                                            pointer-events: none;
                                                            {% endif %}
                                                            {% set rinse_val = states('select.bianca_extra_rinse') %}
                                                            {% if rinse_val != 'Нет' %}
                                                            ha-card {
                                                                background: rgba(76, 175, 80, 0.2);
                                                                border-color: #4CAF50;
                                                            }
                                                            {% endif %}
                                                        {% else %}
                                                        opacity: 0.3;
                                                        pointer-events: none;
                                                        {% endif %}
                                                    }
                                                    ha-card {
                                                        background: var(--card-background-color);
                                                        border: 1px solid var(--divider-color);
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            type: "custom:button-card",
                                            entity: "select.bianca_aqua_plus",
                                            name: "💧",
                                            show_state: true,
                                            tap_action: {
                                                action: "perform-action",
                                                perform_action: "select.select_next",
                                                target: { entity_id: "select.bianca_aqua_plus" },
                                                data: { cycle: true }
                                            },
                                            styles: {
                                                card: [
                                                    {
                                                        "border-radius": "12px",
                                                        "padding": "8px",
                                                        "text-align": "center"
                                                    }
                                                ],
                                                state: [
                                                    {
                                                        "font-size": "11px",
                                                        "font-weight": "bold"
                                                    }
                                                ],
                                                name: [
                                                    {
                                                        "font-size": "16px"
                                                    }
                                                ]
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% set has_aqua = 'Есть' in state_attr('select.bianca_aqua_plus', 'options') %}
                                                            {% if not machine_ready or not has_aqua %}
                                                            opacity: 0.5;
                                                            pointer-events: none;
                                                            {% endif %}
                                                            {% set aqua_val = states('select.bianca_aqua_plus') %}
                                                            {% if aqua_val == 'Есть' %}
                                                            ha-card {
                                                                background: rgba(76, 175, 80, 0.2);
                                                                border-color: #4CAF50;
                                                            }
                                                            {% endif %}
                                                        {% else %}
                                                        opacity: 0.3;
                                                        pointer-events: none;
                                                        {% endif %}
                                                    }
                                                    ha-card {
                                                        background: var(--card-background-color);
                                                        border: 1px solid var(--divider-color);
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            type: "custom:button-card",
                                            entity: "select.bianca_zoom",
                                            name: "🔍",
                                            show_state: true,
                                            tap_action: {
                                                action: "perform-action",
                                                perform_action: "select.select_next",
                                                target: { entity_id: "select.bianca_zoom" },
                                                data: { cycle: true }
                                            },
                                            styles: {
                                                card: [
                                                    {
                                                        "border-radius": "12px",
                                                        "padding": "8px",
                                                        "text-align": "center"
                                                    }
                                                ],
                                                state: [
                                                    {
                                                        "font-size": "11px",
                                                        "font-weight": "bold"
                                                    }
                                                ],
                                                name: [
                                                    {
                                                        "font-size": "16px"
                                                    }
                                                ]
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% set has_zoom = 'Есть' in state_attr('select.bianca_zoom', 'options') %}
                                                            {% if not machine_ready or not has_zoom %}
                                                            opacity: 0.5;
                                                            pointer-events: none;
                                                            {% endif %}
                                                            {% set zoom_val = states('select.bianca_zoom') %}
                                                            {% if zoom_val == 'Есть' %}
                                                            ha-card {
                                                                background: rgba(76, 175, 80, 0.2);
                                                                border-color: #4CAF50;
                                                            }
                                                            {% endif %}
                                                        {% else %}
                                                        opacity: 0.3;
                                                        pointer-events: none;
                                                        {% endif %}
                                                    }
                                                    ha-card {
                                                        background: var(--card-background-color);
                                                        border: 1px solid var(--divider-color);
                                                    }
                                                `
                                            }
                                        }
                                    ]
                                },
                                {
                                    type: "entities",
                                    title: "⏰ Отложенный старт",
                                    show_header_toggle: false,
                                    entities: [
                                        {
                                            entity: "select.bianca_delay_start",
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if not is_state('binary_sensor.bianca_available', 'on') %}
                                                        display: none;
                                                        {% endif %}
                                                        {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                        {% if not machine_ready %}
                                                        opacity: 0.5;
                                                        pointer-events: none;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        };
    }
}

customElements.define('ll-strategy-dashboard-bianca-simple', BiancaSimpleDashboardStrategy);

window.customStrategies = window.customStrategies || [];
window.customStrategies.push({
    type: "bianca-simple",
    strategyType: "dashboard",
    name: "Bianca Simple",
    description: "Упрощённое управление стиральной машиной Bianca",
    documentationURL: "https://github.com/NagibinA/bianca",
});
