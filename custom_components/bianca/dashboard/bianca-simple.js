// BIANCA SIMPLE DASHBOARD STRATEGY - Version 2.4.0
console.log("Loading bianca-simple.js");

class BiancaSimpleDashboardStrategy extends HTMLElement {
    static getCreateSuggestions(_hass) {
        return {
            title: "Bianca Simple",
            icon: "mdi:washing-machine",
        };
    }

    static async generate(config, hass, resources, view) {
        return {
            title: "Bianca",
            views: [
                {
                    title: "Управление",
                    type: "sections",
                    sections: [
                        {
                            type: "grid",
                            cards: [
                                {
                                    square: false,
                                    type: "grid",
                                    columns: 2,
                                    cards: [
                                        {
                                            show_name: true,
                                            show_icon: true,
                                            type: "button",
                                            name: "СТАРТ",
                                            icon: "mdi:play-circle",
                                            tap_action: {
                                                action: "perform-action",
                                                perform_action: "bianca.start_washing"
                                            },
                                            card_mod: {
                                                style: "ha-card { background: #4CAF50; color: white; border-radius: 28px; text-align: center; padding: 12px; } .name { font-weight: bold; font-size: 16px; } .icon { --mdc-icon-size: 32px; color: white; }"
                                            }
                                        },
                                        {
                                            show_name: true,
                                            show_icon: true,
                                            type: "button",
                                            name: "СТОП",
                                            icon: "mdi:stop-circle",
                                            tap_action: {
                                                action: "perform-action",
                                                perform_action: "bianca.stop_washing"
                                            },
                                            show_state: false,
                                            card_mod: {
                                                style: "ha-card { background: #F44336; color: white; border-radius: 28px; text-align: center; padding: 12px; } .name { font-weight: bold; font-size: 16px; } .icon { --mdc-icon-size: 32px; color: white; }"
                                            }
                                        }
                                    ],
                                    grid_options: {
                                        rows: "auto",
                                        columns: 12
                                    }
                                },
                                {
                                    type: "entities",
                                    show_header_toggle: false,
                                    entities: ["select.bianca_program"],
                                    grid_options: {
                                        rows: "auto",
                                        columns: 12
                                    }
                                },
                                {
                                    square: false,
                                    type: "grid",
                                    columns: 2,
                                    cards: [
                                        {
                                            type: "entity",
                                            entity: "sensor.bianca_program_phase",
                                            name: "Фаза"
                                        },
                                        {
                                            type: "entity",
                                            entity: "sensor.bianca_remaining_time",
                                            name: "Осталось"
                                        }
                                    ]
                                },
                                {
                                    type: "horizontal-stack",
                                    cards: [
                                        {
                                            type: "entity",
                                            entity: "select.bianca_temperature",
                                            name: " ",
                                            state_color: true
                                        },
                                        {
                                            type: "entity",
                                            entity: "select.bianca_spin",
                                            name: " ",
                                            state_color: true
                                        },
                                        {
                                            type: "entity",
                                            entity: "select.bianca_steam",
                                            name: " ",
                                            state_color: true
                                        },
                                        {
                                            type: "entity",
                                            entity: "select.bianca_zoom",
                                            name: " ",
                                            state_color: true
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            type: "grid",
                            cards: [
                                {
                                    type: "entities",
                                    show_header_toggle: false,
                                    entities: [{ entity: "select.bianca_temperature" }],
                                    state_color: false
                                },
                                {
                                    type: "entities",
                                    show_header_toggle: false,
                                    entities: [{ entity: "select.bianca_spin" }],
                                    state_color: false
                                },
                                {
                                    type: "entities",
                                    show_header_toggle: false,
                                    entities: [{ entity: "select.bianca_steam" }],
                                    state_color: false
                                },
                                {
                                    type: "entities",
                                    show_header_toggle: false,
                                    entities: [{ entity: "select.bianca_zoom" }],
                                    state_color: false
                                }
                            ]
                        },
                        {
                            type: "grid",
                            cards: [
                                {
                                    type: "entities",
                                    show_header_toggle: false,
                                    entities: ["select.bianca_delay_start"],
                                    state_color: false
                                },
                                {
                                    type: "entities",
                                    show_header_toggle: false,
                                    entities: [{ entity: "select.bianca_hygiene" }],
                                    state_color: false
                                },
                                {
                                    type: "entities",
                                    show_header_toggle: false,
                                    entities: [{ entity: "select.bianca_soil" }],
                                    state_color: false
                                },
                                {
                                    type: "entities",
                                    show_header_toggle: false,
                                    entities: [{ entity: "select.bianca_anti_crease" }],
                                    state_color: false
                                }
                            ]
                        },
                        {
                            type: "grid",
                            cards: [
                                {
                                    type: "entities",
                                    show_header_toggle: false,
                                    entities: [{ entity: "select.bianca_soil" }],
                                    state_color: false
                                },
                                {
                                    type: "entities",
                                    show_header_toggle: false,
                                    entities: [{ entity: "select.bianca_aqua_plus" }],
                                    state_color: false
                                },
                                {
                                    type: "entities",
                                    show_header_toggle: false,
                                    entities: [{ entity: "select.bianca_night_spin" }],
                                    state_color: false
                                },
                                {
                                    type: "entities",
                                    show_header_toggle: false,
                                    entities: [{ entity: "select.bianca_extra_rinse" }],
                                    state_color: false
                                }
                            ]
                        }
                    ]
                }
            ]
        };
    }
}

// Регистрация стратегии
if (!customElements.get('ll-strategy-dashboard-bianca-simple')) {
    customElements.define('ll-strategy-dashboard-bianca-simple', BiancaSimpleDashboardStrategy);
    console.log("Bianca Simple strategy registered");
}

window.customStrategies = window.customStrategies || [];
if (!window.customStrategies.some(s => s.type === "bianca-simple")) {
    window.customStrategies.push({
        type: "bianca-simple",
        strategyType: "dashboard",
        name: "Bianca Simple",
        description: "Упрощённое управление стиральной машиной Bianca"
    });
    console.log("Bianca Simple added to customStrategies");
}
