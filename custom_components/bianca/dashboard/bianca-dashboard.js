class BiancaDashboardStrategy extends HTMLElement {
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
                                    type: "picture-elements",
                                    image: "/local/community/bianca/original.png",
                                    elements: [
                                        {
                                            type: "icon",
                                            icon: "mdi:power",
                                            style: { left: "44.8%", top: "11.2%", "--mdc-icon-size": "49px" },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                        --card-mod-icon-color: cyan;
                                                        {% else %}
                                                        --card-mod-icon-color: grey;
                                                        {% endif %}
                                                        pointer-events: none;
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            type: "icon",
                                            icon: "mdi:thermometer-water",
                                            style: { left: "20%", top: "50%", "--mdc-icon-size": "49px" },
                                            tap_action: {
                                                action: "perform-action",
                                                perform_action: "input_select.select_next",
                                                target: { entity_id: "input_select.bianca_temperature" },
                                                data: { cycle: true }
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                               and is_state('binary_sensor.bianca_available', 'on')
                                                               and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                        {% if machine_ready %}
                                                        --card-mod-icon-color: cyan;
                                                        pointer-events: auto;
                                                        {% else %}
                                                        --card-mod-icon-color: grey;
                                                        pointer-events: none;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            type: "state-label",
                                            entity: "sensor.bianca_temperature",
                                            style: { left: "27%", top: "51%", fontSize: "18px", fontWeight: "bold", color: "cyan" },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if (is_state('sensor.bianca_machine_state', 'Бездействие') or is_state('sensor.bianca_machine_state', 'unavailable'))
                                                              and is_state('binary_sensor.bianca_available', 'on')
                                                              and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                        visibility: hidden;
                                                        {% else %}
                                                        visibility: visible;
                                                        {% endif %}
                                                        pointer-events: none;
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            type: "icon",
                                            icon: "mdi:rotate-right",
                                            style: { left: "11.5%", top: "40.5%", "--mdc-icon-size": "49px" },
                                            tap_action: {
                                                action: "perform-action",
                                                perform_action: "input_select.select_next",
                                                target: { entity_id: "input_select.bianca_spin" },
                                                data: { cycle: true }
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                               and is_state('binary_sensor.bianca_available', 'on')
                                                               and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                        {% if machine_ready %}
                                                        --card-mod-icon-color: cyan;
                                                        pointer-events: auto;
                                                        {% else %}
                                                        --card-mod-icon-color: grey;
                                                        pointer-events: none;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            type: "state-label",
                                            entity: "sensor.bianca_spin_speed",
                                            style: { left: "20%", top: "41%", fontSize: "18px", fontWeight: "bold", color: "cyan" },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if (is_state('sensor.bianca_machine_state', 'Бездействие') or is_state('sensor.bianca_machine_state', 'unavailable'))
                                                              and is_state('binary_sensor.bianca_available', 'on')
                                                              and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                        visibility: hidden;
                                                        {% else %}
                                                        visibility: visible;
                                                        {% endif %}
                                                        pointer-events: none;
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            type: "icon",
                                            icon: "mdi:timer-outline",
                                            style: { left: "11%", top: "30%", "--mdc-icon-size": "49px" },
                                            tap_action: {
                                                action: "perform-action",
                                                perform_action: "input_select.select_next",
                                                target: { entity_id: "input_select.bianca_delay_start" },
                                                data: { cycle: true }
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                               and is_state('binary_sensor.bianca_available', 'on')
                                                               and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                        {% if machine_ready %}
                                                        --card-mod-icon-color: cyan;
                                                        pointer-events: auto;
                                                        {% else %}
                                                        --card-mod-icon-color: grey;
                                                        pointer-events: none;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            type: "state-label",
                                            entity: "sensor.bianca_remaining_time",
                                            style: { left: "32%", top: "33%", fontSize: "18px", fontWeight: "bold", color: "cyan" },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if (is_state('sensor.bianca_machine_state', 'Бездействие') or is_state('sensor.bianca_machine_state', 'unavailable'))
                                                              and is_state('binary_sensor.bianca_available', 'on')
                                                              and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                        visibility: hidden;
                                                        {% else %}
                                                        visibility: visible;
                                                        {% endif %}
                                                        pointer-events: none;
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            type: "state-label",
                                            entity: "sensor.bianca_program_phase",
                                            style: { left: "27%", top: "37.5%", fontSize: "16px", fontWeight: "bold", color: "cyan" },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if (is_state('sensor.bianca_machine_state', 'Бездействие') or is_state('sensor.bianca_machine_state', 'unavailable'))
                                                              and is_state('binary_sensor.bianca_available', 'on')
                                                              and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                        visibility: hidden;
                                                        {% else %}
                                                        visibility: visible;
                                                        {% endif %}
                                                        pointer-events: none;
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            type: "icon",
                                            icon: "mdi:play",
                                            style: { left: "52%", top: "23.6%", "--mdc-icon-size": "52px" },
                                            tap_action: {
                                                action: "perform-action",
                                                perform_action: "bianca.start_washing"
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if is_state('binary_sensor.bianca_available', 'on') 
                                                              and is_state('sensor.bianca_machine_state', 'Бездействие')
                                                              and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                        pointer-events: auto;
                                                        --card-mod-icon-color: white;
                                                        {% elif is_state('binary_sensor.bianca_available', 'on') 
                                                              and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                        pointer-events: none;
                                                        --card-mod-icon-color: cyan;
                                                        {% elif is_state('binary_sensor.bianca_available', 'on') %}
                                                        pointer-events: none;
                                                        --card-mod-icon-color: grey;
                                                        {% else %}
                                                        pointer-events: none;
                                                        --card-mod-icon-color: grey;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            type: "icon",
                                            icon: "mdi:stop",
                                            style: { left: "60%", top: "23.6%", "--mdc-icon-size": "52px" },
                                            tap_action: {
                                                action: "perform-action",
                                                perform_action: "bianca.stop_washing"
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if is_state('binary_sensor.bianca_available', 'on') 
                                                              and is_state('sensor.bianca_machine_state', 'Бездействие')
                                                              and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                        pointer-events: none;
                                                        --card-mod-icon-color: cyan;
                                                        {% elif is_state('binary_sensor.bianca_available', 'on') 
                                                              and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                        pointer-events: auto;
                                                        --card-mod-icon-color: white;
                                                        {% elif is_state('binary_sensor.bianca_available', 'on') %}
                                                        pointer-events: none;
                                                        --card-mod-icon-color: grey;
                                                        {% else %}
                                                        pointer-events: none;
                                                        --card-mod-icon-color: grey;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        }
                                    ]
                                },
                                {
                                    type: "entities",
                                    title: "Состояние",
                                    entities: [
                                        { entity: "binary_sensor.bianca_available", name: "Доступность" },
                                        "sensor.bianca_machine_state",
                                        "sensor.bianca_error",
                                        "sensor.bianca_remote_control"
                                    ]
                                },
                                {
                                    type: "entities",
                                    title: "Параметры",
                                    entities: [
                                        "input_select.bianca_program",
                                        "input_select.bianca_temperature",
                                        "input_select.bianca_spin",
                                        "input_select.bianca_delay_start",
                                        "input_select.bianca_soil",
                                        "input_select.bianca_steam",
                                        "input_select.bianca_pre_wash",
                                        "input_select.bianca_hygiene",
                                        "input_select.bianca_anti_crease",
                                        "input_select.bianca_night_spin",
                                        "input_select.bianca_extra_rinse",
                                        "input_select.bianca_aqua_plus",
                                        "input_select.bianca_zoom"
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

customElements.define('ll-strategy-bianca', BiancaDashboardStrategy);
