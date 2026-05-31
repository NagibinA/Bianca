/**
 * BIANCA DASHBOARD STRATEGY
 * Version: 1.0.20 - Revision 9
 * Date: 2026-05-31
 * 
 * Changes in Revision 9:
 * - Fixed soil level icon logic:
 *   - Perfect 20°C: shows phu:duco-2 (cyan, inactive)
 *   - Programs without soil selection: shows phu:duco-1 (grey, inactive)
 *   - Regular programs: shows active icon with color based on selected value
 * - Fixed font-weight: "font-weight": "bold" (with hyphen)
 * - Removed font-weight from program name
 * - Power icon changed to bianca:power
 * - Icon sizes: 24px for visual indicators, 49px for controls
 * - Added transform: translate(0%, 0%) for all icons
 */

class BiancaDashboardStrategy extends HTMLElement {
    static getCreateSuggestions(_hass) {
        return {
            title: "Bianca",
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
                                    type: "picture-elements",
                                    image: "/local/community/bianca/original.png",
                                    elements: [
                                        // ========== ИКОНКА ПИТАНИЯ ==========
                                        {
                                            type: "icon",
                                            icon: "bianca:power",
                                            style: { 
                                                left: "44.8%", 
                                                top: "11.2%", 
                                                "--mdc-icon-size": "49px",
                                                "transform": "translate(0%, 0%)",
                                                "color": "grey"
                                            },
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
                                        // ========== ИКОНКА WI-FI ==========
                                        {
                                            type: "icon",
                                            icon: "mdi:wifi",
                                            style: { 
                                                left: "30%", 
                                                top: "14%", 
                                                "--mdc-icon-size": "49px",
                                                "transform": "translate(0%, 0%)",
                                                "color": "grey"
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if is_state('binary_sensor.bianca_available', 'on') and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                        --card-mod-icon-color: cyan;
                                                        {% else %}
                                                        --card-mod-icon-color: grey;
                                                        {% endif %}
                                                        pointer-events: none;
                                                    }
                                                `
                                            }
                                        },
                                        // ========== ИКОНКА SET (ПЕРЕБОР ПРОГРАММ) ==========
                                        {
                                            type: "icon",
                                            icon: "bianca:set",
                                            style: { 
                                                left: "35%", 
                                                top: "23.5%", 
                                                "--mdc-icon-size": "65px", 
                                                "opacity": "0.7",
                                                "transform": "translate(0%, 0%)",
                                                "color": "grey"
                                            },
                                            tap_action: {
                                                action: "perform-action",
                                                perform_action: "select.select_next",
                                                target: { entity_id: "select.bianca_program" },
                                                data: { cycle: true }
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                               and is_state('binary_sensor.bianca_available', 'on')
                                                               and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                        {% if machine_ready %}
                                                        pointer-events: auto;
                                                        --card-mod-icon-color: cyan;
                                                        {% else %}
                                                        pointer-events: none;
                                                        --card-mod-icon-color: grey;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        },
                                        // ========== НАЗВАНИЕ ПРОГРАММЫ (ВЫБРАННОЕ) ==========
                                        {
                                            type: "state-label",
                                            entity: "select.bianca_program",
                                            style: { 
                                                left: "50%", 
                                                top: "49%"
                                            },
                                            tap_action: { action: "none" },
                                            hold_action: { action: "more-info" },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                               and is_state('binary_sensor.bianca_available', 'on')
                                                               and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                        {% if machine_ready %}
                                                        visibility: visible;
                                                        color: cyan;
                                                        pointer-events: auto;
                                                        {% else %}
                                                        visibility: hidden;
                                                        pointer-events: none;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        },
                                        // ========== ИКОНКА ХЛОПОК 1 ==========
                                        {
                                            type: "icon",
                                            icon: "bianca:cotton-1",
                                            style: { 
                                                left: "60.5%", 
                                                top: "13.2%", 
                                                "--mdc-icon-size": "49px",
                                                "transform": "translate(0%, 0%)",
                                                "color": "grey"
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% set prog_num = state_attr('sensor.bianca_program', 'program_number') %}
                                                        {% if prog_num == 1 %}
                                                        --card-mod-icon-color: cyan;
                                                        {% else %}
                                                        --card-mod-icon-color: grey;
                                                        {% endif %}
                                                        pointer-events: none;
                                                    }
                                                `
                                            }
                                        },
                                        // ========== ИКОНКА ХЛОПОК 2 ==========
                                        {
                                            type: "icon",
                                            icon: "bianca:cotton-2",
                                            style: { 
                                                left: "71%", 
                                                top: "20.5%", 
                                                "--mdc-icon-size": "49px",
                                                "transform": "translate(0%, 0%)",
                                                "color": "grey"
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% set prog_num = state_attr('sensor.bianca_program', 'program_number') %}
                                                        {% if prog_num == 2 %}
                                                        --card-mod-icon-color: cyan;
                                                        {% else %}
                                                        --card-mod-icon-color: grey;
                                                        {% endif %}
                                                        pointer-events: none;
                                                    }
                                                `
                                            }
                                        },
                                        // ========== ИКОНКА СИНТЕТИКА ==========
                                        {
                                            type: "icon",
                                            icon: "bianca:synthetics",
                                            style: { 
                                                left: "78%", 
                                                top: "29.7%", 
                                                "--mdc-icon-size": "49px",
                                                "transform": "translate(0%, 0%)",
                                                "color": "grey"
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% set prog_num = state_attr('sensor.bianca_program', 'program_number') %}
                                                        {% if prog_num == 3 %}
                                                        --card-mod-icon-color: cyan;
                                                        {% else %}
                                                        --card-mod-icon-color: grey;
                                                        {% endif %}
                                                        pointer-events: none;
                                                    }
                                                `
                                            }
                                        },
                                        // ========== ИКОНКА ШЕРСТЬ ==========
                                        {
                                            type: "icon",
                                            icon: "bianca:wool",
                                            style: { 
                                                left: "78%", 
                                                top: "40.5%", 
                                                "--mdc-icon-size": "49px",
                                                "transform": "translate(0%, 0%)",
                                                "color": "grey"
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% set prog_num = state_attr('sensor.bianca_program', 'program_number') %}
                                                        {% if prog_num == 4 %}
                                                        --card-mod-icon-color: cyan;
                                                        {% else %}
                                                        --card-mod-icon-color: grey;
                                                        {% endif %}
                                                        pointer-events: none;
                                                    }
                                                `
                                            }
                                        },
                                        // ========== ИКОНКА ДЕЛИКАТНАЯ ==========
                                        {
                                            type: "icon",
                                            icon: "bianca:delicate",
                                            style: { 
                                                left: "71.5%", 
                                                top: "49.5%", 
                                                "--mdc-icon-size": "49px",
                                                "transform": "translate(0%, 0%)",
                                                "color": "grey"
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% set prog_num = state_attr('sensor.bianca_program', 'program_number') %}
                                                        {% if prog_num == 5 %}
                                                        --card-mod-icon-color: cyan;
                                                        {% else %}
                                                        --card-mod-icon-color: grey;
                                                        {% endif %}
                                                        pointer-events: none;
                                                    }
                                                `
                                            }
                                        },
                                        // ========== ИКОНКА PERFECT 20°C ==========
                                        {
                                            type: "icon",
                                            icon: "bianca:perfect20",
                                            style: { 
                                                left: "59%", 
                                                top: "56.5%", 
                                                "--mdc-icon-size": "49px",
                                                "transform": "translate(0%, 0%)",
                                                "color": "grey"
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% set prog_num = state_attr('sensor.bianca_program', 'program_number') %}
                                                        {% if prog_num == 6 %}
                                                        --card-mod-icon-color: cyan;
                                                        {% else %}
                                                        --card-mod-icon-color: grey;
                                                        {% endif %}
                                                        pointer-events: none;
                                                    }
                                                `
                                            }
                                        },
                                        // ========== ИКОНКА ПОЛОСКАНИЕ ==========
                                        {
                                            type: "icon",
                                            icon: "bianca:rinsing",
                                            style: { 
                                                left: "45%", 
                                                top: "58.8%", 
                                                "--mdc-icon-size": "49px",
                                                "transform": "translate(0%, 0%)",
                                                "color": "grey"
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% set prog_num = state_attr('sensor.bianca_program', 'program_number') %}
                                                        {% if prog_num == 7 %}
                                                        --card-mod-icon-color: cyan;
                                                        {% else %}
                                                        --card-mod-icon-color: grey;
                                                        {% endif %}
                                                        pointer-events: none;
                                                    }
                                                `
                                            }
                                        },
                                        // ========== ИКОНКА СЛИВ + ОТЖИМ ==========
                                        {
                                            type: "icon",
                                            icon: "bianca:draining",
                                            style: { 
                                                left: "30%", 
                                                top: "56.5%", 
                                                "--mdc-icon-size": "49px",
                                                "transform": "translate(0%, 0%)",
                                                "color": "grey"
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% set prog_num = state_attr('sensor.bianca_program', 'program_number') %}
                                                        {% if prog_num == 8 %}
                                                        --card-mod-icon-color: cyan;
                                                        {% else %}
                                                        --card-mod-icon-color: grey;
                                                        {% endif %}
                                                        pointer-events: none;
                                                    }
                                                `
                                            }
                                        },
                                        // ========== РАБОЧАЯ ТЕМПЕРАТУРА ==========
                                        {
                                            type: "state-label",
                                            entity: "sensor.bianca_temperature",
                                            style: { 
                                                left: "27%", 
                                                top: "51%", 
                                                fontSize: "18px", 
                                                "font-weight": "bold", 
                                                color: "cyan",
                                                "transform": "translate(0%, 0%)"
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                               and is_state('binary_sensor.bianca_available', 'on')
                                                               and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                        {% if machine_ready %}
                                                        visibility: hidden;
                                                        {% else %}
                                                        visibility: visible;
                                                        {% endif %}
                                                        pointer-events: none;
                                                    }
                                                `
                                            }
                                        },
                                        // ========== ВЫБРАННАЯ ТЕМПЕРАТУРА ==========
                                        {
                                            type: "state-label",
                                            entity: "select.bianca_temperature",
                                            style: { 
                                                left: "62%", 
                                                top: "38%", 
                                                fontSize: "18px", 
                                                "font-weight": "bold", 
                                                color: "cyan",
                                                "transform": "translate(0%, 0%)"
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                               and is_state('binary_sensor.bianca_available', 'on')
                                                               and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                        {% if machine_ready %}
                                                        visibility: visible;
                                                        {% else %}
                                                        visibility: hidden;
                                                        {% endif %}
                                                        pointer-events: none;
                                                    }
                                                `
                                            }
                                        },
                                        // ========== ИКОНКА ТЕМПЕРАТУРЫ ==========
                                        {
                                            type: "icon",
                                            icon: "mdi:thermometer-water",
                                            style: { 
                                                left: "20%", 
                                                top: "50%", 
                                                "--mdc-icon-size": "49px",
                                                "transform": "translate(0%, 0%)",
                                                "color": "grey"
                                            },
                                            tap_action: {
                                                action: "perform-action",
                                                perform_action: "select.select_next",
                                                target: { entity_id: "select.bianca_temperature" },
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
                                        // ========== РАБОЧИЙ ОТЖИМ ==========
                                        {
                                            type: "state-label",
                                            entity: "sensor.bianca_spin_speed",
                                            style: { 
                                                left: "20%", 
                                                top: "41%", 
                                                fontSize: "18px", 
                                                "font-weight": "bold", 
                                                color: "cyan",
                                                "transform": "translate(0%, 0%)"
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                               and is_state('binary_sensor.bianca_available', 'on')
                                                               and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                        {% if machine_ready %}
                                                        visibility: hidden;
                                                        {% else %}
                                                        visibility: visible;
                                                        {% endif %}
                                                        pointer-events: none;
                                                    }
                                                `
                                            }
                                        },
                                        // ========== ВЫБРАННЫЙ ОТЖИМ ==========
                                        {
                                            type: "state-label",
                                            entity: "select.bianca_spin",
                                            style: { 
                                                left: "48%", 
                                                top: "33%", 
                                                fontSize: "18px", 
                                                "font-weight": "bold", 
                                                color: "cyan",
                                                "transform": "translate(0%, 0%)"
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                               and is_state('binary_sensor.bianca_available', 'on')
                                                               and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                        {% if machine_ready %}
                                                        visibility: visible;
                                                        {% else %}
                                                        visibility: hidden;
                                                        {% endif %}
                                                        pointer-events: none;
                                                    }
                                                `
                                            }
                                        },
                                        // ========== ИКОНКА ОТЖИМА ==========
                                        {
                                            type: "icon",
                                            icon: "bianca:spin",
                                            style: { 
                                                left: "11.5%", 
                                                top: "40.5%", 
                                                "--mdc-icon-size": "49px",
                                                "transform": "translate(0%, 0%)",
                                                "color": "grey"
                                            },
                                            tap_action: {
                                                action: "perform-action",
                                                perform_action: "select.select_next",
                                                target: { entity_id: "select.bianca_spin" },
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
                                        // ========== ОСТАВШЕЕСЯ ВРЕМЯ ==========
                                        {
                                            type: "state-label",
                                            entity: "sensor.bianca_remaining_time",
                                            style: { 
                                                left: "32%", 
                                                top: "33%", 
                                                fontSize: "18px", 
                                                "font-weight": "bold", 
                                                color: "cyan",
                                                "transform": "translate(0%, 0%)"
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                               and is_state('binary_sensor.bianca_available', 'on')
                                                               and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                        {% if machine_ready %}
                                                        visibility: hidden;
                                                        {% else %}
                                                        visibility: visible;
                                                        {% endif %}
                                                        pointer-events: none;
                                                    }
                                                `
                                            }
                                        },
                                        // ========== ВЫБРАННАЯ ЗАДЕРЖКА ==========
                                        {
                                            type: "state-label",
                                            entity: "select.bianca_delay_start",
                                            style: { 
                                                left: "25%", 
                                                top: "38%", 
                                                fontSize: "18px", 
                                                "font-weight": "bold", 
                                                color: "cyan",
                                                "transform": "translate(0%, 0%)"
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                               and is_state('binary_sensor.bianca_available', 'on')
                                                               and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                        {% if machine_ready %}
                                                        visibility: visible;
                                                        {% else %}
                                                        visibility: hidden;
                                                        {% endif %}
                                                        pointer-events: none;
                                                    }
                                                `
                                            }
                                        },
                                        // ========== ИКОНКА ЗАДЕРЖКИ ==========
                                        {
                                            type: "icon",
                                            icon: "bianca:delay",
                                            style: { 
                                                left: "11%", 
                                                top: "30%", 
                                                "--mdc-icon-size": "49px",
                                                "transform": "translate(0%, 0%)",
                                                "color": "grey"
                                            },
                                            tap_action: {
                                                action: "perform-action",
                                                perform_action: "select.select_next",
                                                target: { entity_id: "select.bianca_delay_start" },
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
                                        // ========== ФАЗА ПРОГРАММЫ ==========
                                        {
                                            type: "state-label",
                                            entity: "sensor.bianca_program_phase",
                                            style: { 
                                                left: "27%", 
                                                top: "37.5%", 
                                                fontSize: "16px", 
                                                "font-weight": "bold", 
                                                color: "cyan",
                                                "transform": "translate(0%, 0%)"
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                               and is_state('binary_sensor.bianca_available', 'on')
                                                               and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                        {% if machine_ready %}
                                                        visibility: hidden;
                                                        {% else %}
                                                        visibility: visible;
                                                        {% endif %}
                                                        pointer-events: none;
                                                    }
                                                `
                                            }
                                        },
                                        // ========== ИКОНКА ПАРА ==========
                                        {
                                            type: "icon",
                                            icon: "bianca:steam-1",
                                            style: { 
                                                left: "18%", 
                                                top: "20%", 
                                                "--mdc-icon-size": "49px",
                                                "transform": "translate(0%, 0%)",
                                                "color": "grey"
                                            },
                                            tap_action: {
                                                action: "perform-action",
                                                perform_action: "select.select_next",
                                                target: { entity_id: "select.bianca_steam" },
                                                data: { cycle: true }
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                               and is_state('binary_sensor.bianca_available', 'on')
                                                               and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                        {% set steam_val = states('select.bianca_steam') %}
                                                        {% if machine_ready %}
                                                        pointer-events: auto;
                                                        --card-mod-icon-color: {{ 'cyan' if steam_val == 'С паром' else 'grey' }};
                                                        {% else %}
                                                        pointer-events: none;
                                                        --card-mod-icon-color: grey;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        },
                                        // ========== ИКОНКА УРОВНЯ ЗАГРЯЗНЕНИЯ ==========
                                        {
                                            type: "icon",
                                            icon: "phu:duco-1",
                                            style: { 
                                                left: "25%", 
                                                top: "44.2%", 
                                                "--mdc-icon-size": "24px",
                                                "transform": "translate(0%, 0%)",
                                                "color": "grey"
                                            },
                                            tap_action: {
                                                action: "perform-action",
                                                perform_action: "select.select_next",
                                                target: { entity_id: "select.bianca_soil" },
                                                data: { cycle: true }
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                               and is_state('binary_sensor.bianca_available', 'on')
                                                               and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                        {% set soil_val = states('select.bianca_soil') %}
                                                        {% set program = states('select.bianca_program') %}
                                                        
                                                        {# Perfect 20°C - только Нормально, иконка phu:duco-2 #}
                                                        {% if program == 'Perfect 20°C' %}
                                                        --card-mod-icon: phu:duco-2;
                                                        --card-mod-icon-color: cyan;
                                                        pointer-events: none;
                                                        
                                                        {# Программы без выбора загрязнения - только Нет, иконка серая #}
                                                        {% elif program in ['Шерсть', 'Деликатная', 'Полоскание', 'Слив + Отжим', 'Сохранить свежесть', 'Perfect rapid 59 минут'] %}
                                                        --card-mod-icon: phu:duco-1;
                                                        --card-mod-icon-color: grey;
                                                        pointer-events: none;
                                                        
                                                        {# Остальные программы - можно выбирать #}
                                                        {% else %}
                                                            {% if machine_ready %}
                                                            pointer-events: auto;
                                                            {% else %}
                                                            pointer-events: none;
                                                            {% endif %}
                                                            
                                                            {% if soil_val == 'Мало' %}
                                                            --card-mod-icon: phu:duco-1;
                                                            --card-mod-icon-color: cyan;
                                                            {% elif soil_val == 'Нормально' %}
                                                            --card-mod-icon: phu:duco-2;
                                                            --card-mod-icon-color: cyan;
                                                            {% elif soil_val == 'Очень' %}
                                                            --card-mod-icon: phu:duco-3;
                                                            --card-mod-icon-color: cyan;
                                                            {% else %}
                                                            --card-mod-icon: phu:duco-1;
                                                            --card-mod-icon-color: grey;
                                                            {% endif %}
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        },
                                        // ========== ИКОНКА ПРЕДВАРИТЕЛЬНОЙ СТИРКИ ==========
                                        {
                                            type: "icon",
                                            icon: "bianca:pre-wash",
                                            style: { 
                                                left: "31.7%", 
                                                top: "44.2%", 
                                                "--mdc-icon-size": "24px",
                                                "transform": "translate(0%, 0%)",
                                                "color": "grey"
                                            },
                                            tap_action: {
                                                action: "perform-action",
                                                perform_action: "select.select_next",
                                                target: { entity_id: "select.bianca_pre_wash" },
                                                data: { cycle: true }
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                               and is_state('binary_sensor.bianca_available', 'on')
                                                               and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                        {% set prewash_val = states('select.bianca_pre_wash') %}
                                                        {% if machine_ready and prewash_val in ['Есть', 'Нет'] %}
                                                        visibility: visible;
                                                        pointer-events: auto;
                                                        --card-mod-icon-color: {{ 'cyan' if prewash_val == 'Есть' else 'grey' }};
                                                        {% else %}
                                                        visibility: hidden;
                                                        pointer-events: none;
                                                        --card-mod-icon-color: grey;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        },
                                        // ========== ИКОНКА ГИГИЕНЫ ==========
                                        {
                                            type: "icon",
                                            icon: "bianca:hygiene-wash",
                                            style: { 
                                                left: "39%", 
                                                top: "44.2%", 
                                                "--mdc-icon-size": "24px",
                                                "transform": "translate(0%, 0%)",
                                                "color": "grey"
                                            },
                                            tap_action: {
                                                action: "perform-action",
                                                perform_action: "select.select_next",
                                                target: { entity_id: "select.bianca_hygiene" },
                                                data: { cycle: true }
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                               and is_state('binary_sensor.bianca_available', 'on')
                                                               and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                        {% set hygiene_val = states('select.bianca_hygiene') %}
                                                        {% if machine_ready and hygiene_val in ['Есть', 'Нет'] %}
                                                        visibility: visible;
                                                        pointer-events: auto;
                                                        --card-mod-icon-color: {{ 'cyan' if hygiene_val == 'Есть' else 'grey' }};
                                                        {% else %}
                                                        visibility: hidden;
                                                        pointer-events: none;
                                                        --card-mod-icon-color: grey;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        },
                                        // ========== ИКОНКА АНТИСМИНАНИЯ ==========
                                        {
                                            type: "icon",
                                            icon: "bianca:anti-crease",
                                            style: { 
                                                left: "46.6%", 
                                                top: "44.2%", 
                                                "--mdc-icon-size": "24px",
                                                "transform": "translate(0%, 0%)",
                                                "color": "grey"
                                            },
                                            tap_action: {
                                                action: "perform-action",
                                                perform_action: "select.select_next",
                                                target: { entity_id: "select.bianca_anti_crease" },
                                                data: { cycle: true }
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                               and is_state('binary_sensor.bianca_available', 'on')
                                                               and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                        {% set anticrease_val = states('select.bianca_anti_crease') %}
                                                        {% if machine_ready and anticrease_val in ['Есть', 'Нет'] %}
                                                        visibility: visible;
                                                        pointer-events: auto;
                                                        --card-mod-icon-color: {{ 'cyan' if anticrease_val == 'Есть' else 'grey' }};
                                                        {% else %}
                                                        visibility: hidden;
                                                        pointer-events: none;
                                                        --card-mod-icon-color: grey;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        },
                                        // ========== ИКОНКА НОЧНОЙ СТИРКИ ==========
                                        {
                                            type: "icon",
                                            icon: "bianca:night-spin",
                                            style: { 
                                                left: "55%", 
                                                top: "44.2%", 
                                                "--mdc-icon-size": "24px",
                                                "transform": "translate(0%, 0%)",
                                                "color": "grey"
                                            },
                                            tap_action: {
                                                action: "perform-action",
                                                perform_action: "select.select_next",
                                                target: { entity_id: "select.bianca_night_spin" },
                                                data: { cycle: true }
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                               and is_state('binary_sensor.bianca_available', 'on')
                                                               and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                        {% set nightspin_val = states('select.bianca_night_spin') %}
                                                        {% if machine_ready and nightspin_val in ['Есть', 'Нет'] %}
                                                        visibility: visible;
                                                        pointer-events: auto;
                                                        --card-mod-icon-color: {{ 'cyan' if nightspin_val == 'Есть' else 'grey' }};
                                                        {% else %}
                                                        visibility: hidden;
                                                        pointer-events: none;
                                                        --card-mod-icon-color: grey;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        },
                                        // ========== ИКОНКА ДОПОЛНИТЕЛЬНЫХ ПОЛОСКАНИЙ ==========
                                        {
                                            type: "icon",
                                            icon: "bianca:rinse-1",
                                            style: { 
                                                left: "62%", 
                                                top: "44.2%", 
                                                "--mdc-icon-size": "24px",
                                                "transform": "translate(0%, 0%)",
                                                "color": "grey"
                                            },
                                            tap_action: {
                                                action: "perform-action",
                                                perform_action: "select.select_next",
                                                target: { entity_id: "select.bianca_extra_rinse" },
                                                data: { cycle: true }
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                               and is_state('binary_sensor.bianca_available', 'on')
                                                               and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                        {% set rinse_val = states('select.bianca_extra_rinse') %}
                                                        {% if machine_ready %}
                                                        visibility: visible;
                                                        pointer-events: auto;
                                                        {% if rinse_val == '1 полоскание' %}
                                                        --card-mod-icon-color: cyan;
                                                        {% elif rinse_val == '2 полоскания' %}
                                                        --card-mod-icon: bianca:rinse-2;
                                                        --card-mod-icon-color: cyan;
                                                        {% elif rinse_val == '3 полоскания' %}
                                                        --card-mod-icon: bianca:rinse-3;
                                                        --card-mod-icon-color: cyan;
                                                        {% else %}
                                                        --card-mod-icon-color: grey;
                                                        {% endif %}
                                                        {% else %}
                                                        visibility: hidden;
                                                        pointer-events: none;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        },
                                        // ========== ИКОНКА АКВАПЛЮС ==========
                                        {
                                            type: "icon",
                                            icon: "bianca:extra-water",
                                            style: { 
                                                left: "68.5%", 
                                                top: "44.2%", 
                                                "--mdc-icon-size": "24px",
                                                "transform": "translate(0%, 0%)",
                                                "color": "grey"
                                            },
                                            tap_action: {
                                                action: "perform-action",
                                                perform_action: "select.select_next",
                                                target: { entity_id: "select.bianca_aqua_plus" },
                                                data: { cycle: true }
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                               and is_state('binary_sensor.bianca_available', 'on')
                                                               and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                        {% set aquaplus_val = states('select.bianca_aqua_plus') %}
                                                        {% if machine_ready %}
                                                        visibility: visible;
                                                        pointer-events: auto;
                                                        --card-mod-icon-color: {{ 'cyan' if aquaplus_val == 'Есть' else 'grey' }};
                                                        {% else %}
                                                        visibility: hidden;
                                                        pointer-events: none;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        },
                                        // ========== ИКОНКА ZOOM ==========
                                        {
                                            type: "icon",
                                            icon: "bianca:zoom",
                                            style: { 
                                                left: "38%", 
                                                top: "47%", 
                                                "--mdc-icon-size": "110px",
                                                "transform": "translate(0%, 0%)",
                                                "color": "grey"
                                            },
                                            tap_action: {
                                                action: "perform-action",
                                                perform_action: "select.select_next",
                                                target: { entity_id: "select.bianca_zoom" },
                                                data: { cycle: true }
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% set remote_off = is_state('sensor.bianca_remote_control', 'Выкл') %}
                                                        {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                               and is_state('binary_sensor.bianca_available', 'on') %}
                                                        {% set zoom_on = is_state('select.bianca_zoom', 'Есть') %}
                                                        {% if remote_off %}
                                                        --card-mod-icon-color: {{ 'cyan' if zoom_on else 'grey' }};
                                                        pointer-events: none;
                                                        {% elif machine_ready %}
                                                        pointer-events: auto;
                                                        {% set select_val = states('select.bianca_zoom') %}
                                                        --card-mod-icon-color: {{ 'cyan' if select_val == 'Есть' else 'grey' }};
                                                        {% else %}
                                                        --card-mod-icon-color: {{ 'cyan' if zoom_on else 'grey' }};
                                                        pointer-events: none;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        },
                                        // ========== КНОПКА PLAY ==========
                                        {
                                            type: "icon",
                                            icon: "mdi:play",
                                            style: { 
                                                left: "52%", 
                                                top: "23.6%", 
                                                "--mdc-icon-size": "52px",
                                                "transform": "translate(0%, 0%)",
                                                "color": "grey"
                                            },
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
                                        // ========== КНОПКА STOP ==========
                                        {
                                            type: "icon",
                                            icon: "mdi:stop",
                                            style: { 
                                                left: "60%", 
                                                top: "23.6%", 
                                                "--mdc-icon-size": "52px",
                                                "transform": "translate(0%, 0%)",
                                                "color": "grey"
                                            },
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
                                // ========== КАРТОЧКА СОСТОЯНИЯ ==========
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
                                // ========== КАРТОЧКА ПАРАМЕТРОВ ==========
                                {
                                    type: "entities",
                                    title: "Параметры",
                                    entities: [
                                        "select.bianca_program",
                                        "select.bianca_temperature",
                                        "select.bianca_spin",
                                        "select.bianca_delay_start",
                                        "select.bianca_soil",
                                        "select.bianca_steam",
                                        "select.bianca_pre_wash",
                                        "select.bianca_hygiene",
                                        "select.bianca_anti_crease",
                                        "select.bianca_night_spin",
                                        "select.bianca_extra_rinse",
                                        "select.bianca_aqua_plus",
                                        "select.bianca_zoom"
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

customElements.define('ll-strategy-dashboard-bianca', BiancaDashboardStrategy);

window.customStrategies = window.customStrategies || [];
window.customStrategies.push({
    type: "bianca",
    strategyType: "dashboard",
    name: "Bianca",
    description: "Управление стиральной машиной Bianca",
    documentationURL: "https://github.com/NagibinA/bianca",
});
