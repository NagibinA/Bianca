/**
 * BIANCA SIMPLE DASHBOARD STRATEGY
 * Version: 1.0.1
 * Упрощённая панель управления с горизонтальным расположением
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
                                // Статус онлайн/офлайн
                                {
                                    type: "entity",
                                    entity: "binary_sensor.bianca_available",
                                    name: "Bianca",
                                    icon: "mdi:washing-machine",
                                    card_mod: {
                                        style: `
                                            ha-card {
                                                {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                border-left: 4px solid #4CAF50;
                                                {% else %}
                                                border-left: 4px solid #9E9E9E;
                                                {% endif %}
                                            }
                                        `
                                    }
                                },
                                // Кнопки СТАРТ и СТОП в ряд
                                {
                                    type: "grid",
                                    columns: 2,
                                    cards: [
                                        {
                                            type: "button",
                                            name: "СТАРТ",
                                            icon: "mdi:play-circle",
                                            tap_action: {
                                                action: "perform-action",
                                                perform_action: "bianca.start_washing"
                                            },
                                            card_mod: {
                                                style: `
                                                    ha-card {
                                                        background: rgba(76, 175, 80, 0.15);
                                                        color: #4CAF50;
                                                        border-radius: 16px;
                                                        text-align: center;
                                                    }
                                                    ha-card:active {
                                                        background: rgba(76, 175, 80, 0.3);
                                                    }
                                                    .name {
                                                        font-weight: bold;
                                                        font-size: 16px;
                                                    }
                                                    .icon {
                                                        --mdc-icon-size: 36px;
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            type: "button",
                                            name: "СТОП",
                                            icon: "mdi:stop-circle",
                                            tap_action: {
                                                action: "perform-action",
                                                perform_action: "bianca.stop_washing"
                                            },
                                            card_mod: {
                                                style: `
                                                    ha-card {
                                                        background: rgba(244, 67, 54, 0.15);
                                                        color: #F44336;
                                                        border-radius: 16px;
                                                        text-align: center;
                                                    }
                                                    .name {
                                                        font-weight: bold;
                                                        font-size: 16px;
                                                    }
                                                    .icon {
                                                        --mdc-icon-size: 36px;
                                                    }
                                                `
                                            }
                                        }
                                    ]
                                },
                                // Программа
                                {
                                    type: "entities",
                                    title: "📋 ПРОГРАММА",
                                    show_header_toggle: false,
                                    entities: ["select.bianca_program"]
                                },
                                // Оставшееся время и фаза (в ряд)
                                {
                                    type: "grid",
                                    columns: 2,
                                    cards: [
                                        {
                                            type: "entity",
                                            entity: "sensor.bianca_remaining_time",
                                            name: "⏱️ Осталось",
                                            card_mod: {
                                                style: `
                                                    ha-card {
                                                        text-align: center;
                                                        background: var(--card-background-color);
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            type: "entity",
                                            entity: "sensor.bianca_program_phase",
                                            name: "🔧 Фаза",
                                            card_mod: {
                                                style: `
                                                    ha-card {
                                                        text-align: center;
                                                    }
                                                `
                                            }
                                        }
                                    ]
                                },
                                // ОПЦИИ - заголовок
                                {
                                    type: "entities",
                                    title: "⚙️ ОПЦИИ",
                                    show_header_toggle: false,
                                    entities: []
                                },
                                // Опции в 3 колонки
                                {
                                    type: "grid",
                                    columns: 3,
                                    cards: [
                                        {
                                            type: "entity",
                                            entity: "select.bianca_temperature",
                                            name: "🌡️ Температура",
                                            card_mod: {
                                                style: `
                                                    ha-card {
                                                        text-align: center;
                                                        padding: 4px;
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            type: "entity",
                                            entity: "select.bianca_spin",
                                            name: "🔄 Отжим",
                                            card_mod: {
                                                style: `
                                                    ha-card {
                                                        text-align: center;
                                                        padding: 4px;
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            type: "entity",
                                            entity: "select.bianca_soil",
                                            name: "💧 Загрязнение",
                                            card_mod: {
                                                style: `
                                                    ha-card {
                                                        text-align: center;
                                                        padding: 4px;
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            type: "entity",
                                            entity: "select.bianca_steam",
                                            name: "💨 Пар",
                                            card_mod: {
                                                style: `
                                                    ha-card {
                                                        text-align: center;
                                                        padding: 4px;
                                                    }
                                                `
                                            }
                                        }
                                    ]
                                },
                                // Дополнительные опции в 4 колонки
                                {
                                    type: "grid",
                                    columns: 4,
                                    cards: [
                                        {
                                            type: "entity",
                                            entity: "select.bianca_pre_wash",
                                            name: "🧼 Пред.",
                                            card_mod: {
                                                style: `
                                                    ha-card {
                                                        text-align: center;
                                                        padding: 4px;
                                                        font-size: 12px;
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            type: "entity",
                                            entity: "select.bianca_hygiene",
                                            name: "🦠 Гигиена",
                                            card_mod: {
                                                style: `
                                                    ha-card {
                                                        text-align: center;
                                                        padding: 4px;
                                                        font-size: 12px;
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            type: "entity",
                                            entity: "select.bianca_anti_crease",
                                            name: "↩️ Антисм.",
                                            card_mod: {
                                                style: `
                                                    ha-card {
                                                        text-align: center;
                                                        padding: 4px;
                                                        font-size: 12px;
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            type: "entity",
                                            entity: "select.bianca_night_spin",
                                            name: "🌙 Ночная",
                                            card_mod: {
                                                style: `
                                                    ha-card {
                                                        text-align: center;
                                                        padding: 4px;
                                                        font-size: 12px;
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            type: "entity",
                                            entity: "select.bianca_extra_rinse",
                                            name: "💦 Полоск.",
                                            card_mod: {
                                                style: `
                                                    ha-card {
                                                        text-align: center;
                                                        padding: 4px;
                                                        font-size: 12px;
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            type: "entity",
                                            entity: "select.bianca_aqua_plus",
                                            name: "💧 Аква+",
                                            card_mod: {
                                                style: `
                                                    ha-card {
                                                        text-align: center;
                                                        padding: 4px;
                                                        font-size: 12px;
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            type: "entity",
                                            entity: "select.bianca_zoom",
                                            name: "🔍 Zoom",
                                            card_mod: {
                                                style: `
                                                    ha-card {
                                                        text-align: center;
                                                        padding: 4px;
                                                        font-size: 12px;
                                                    }
                                                `
                                            }
                                        }
                                    ]
                                },
                                // Отложенный старт
                                {
                                    type: "entities",
                                    title: "⏰ Отложенный старт",
                                    show_header_toggle: false,
                                    entities: ["select.bianca_delay_start"]
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
