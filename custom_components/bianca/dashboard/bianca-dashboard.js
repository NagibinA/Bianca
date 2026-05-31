/**
 * BIANCA DASHBOARD STRATEGY
 * Version: 1.0.22 - Revision 1
 * Date: 2026-06-01
 * 
 * Changes in this version:
 * - Fixed Play/Stop buttons behavior with remote_control check
 * - Icons are hidden when their value is disabled/off
 * - Steam and Zoom always visible
 * - All icons show actual values during washing (from sensors)
 * - All icons show selected values during selection mode (from selects)
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
                                        // ========== СООБЩЕНИЕ ОБ ОШИБКЕ ==========
                                        {
                                            type: "state-label",
                                            entity: "sensor.bianca_error",
                                            style: { 
                                                left: "25%", 
                                                top: "29.5%", 
                                                "font-size": "14px", 
                                                "font-weight": "bold", 
                                                color: "red",
                                                "transform": "translate(0%, 0%)"
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% set washer_on = is_state('binary_sensor.bianca_available', 'on') %}
                                                        {% set error_status = states('sensor.bianca_error') %}
                                                        {% set has_no_errors = error_status == 'Нет ошибок' %}
                                                        {% set is_available = error_status != 'unavailable' %}
                                                        
                                                        {% if washer_on and has_no_errors %}
                                                        visibility: hidden;
                                                        {% elif washer_on and is_available %}
                                                        visibility: visible;
                                                        {% else %}
                                                        visibility: hidden;
                                                        {% endif %}
                                                        pointer-events: none;
                                                    }
                                                `
                                            }
                                        },
                                        // ========== ОБРАТНЫЙ ОТСЧЕТ (ОТЛОЖЕННЫЙ СТАРТ) ==========
                                        {
                                            type: "state-label",
                                            entity: "sensor.bianca_delay_countdown",
                                            style: { 
                                                left: "45%", 
                                                top: "33%", 
                                                "font-size": "18px", 
                                                "font-weight": "bold", 
                                                color: "blue",
                                                "transform": "translate(0%, 0%)"
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_state = states('sensor.bianca_machine_state') %}
                                                            {% if machine_state == 'Задан отложенный запуск' %}
                                                            visibility: visible;
                                                            {% else %}
                                                            visibility: hidden;
                                                            {% endif %}
                                                        {% else %}
                                                            visibility: hidden;
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
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                                   and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% if machine_ready %}
                                                            pointer-events: auto;
                                                            --card-mod-icon-color: cyan;
                                                            {% else %}
                                                            pointer-events: none;
                                                            --card-mod-icon-color: grey;
                                                            {% endif %}
                                                        {% else %}
                                                            --card-mod-icon-color: grey;
                                                            pointer-events: none;
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
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                                   and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% if machine_ready %}
                                                            visibility: visible;
                                                            color: cyan;
                                                            pointer-events: auto;
                                                            {% else %}
                                                            visibility: hidden;
                                                            pointer-events: none;
                                                            {% endif %}
                                                        {% else %}
                                                            visibility: hidden;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        },
                                        // ========== ИКОНКИ ПРОГРАММ (ИНФОРМАТИВНЫЕ, НЕ КЛИКАБЕЛЬНЫЕ) ==========
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
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set program = states('sensor.bianca_program') %}
                                                            {% if program == 'Хлопок: Интенсивная стирка' %}
                                                            --card-mod-icon-color: cyan;
                                                            {% else %}
                                                            --card-mod-icon-color: grey;
                                                            {% endif %}
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
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set program = states('sensor.bianca_program') %}
                                                            {% if program == 'Хлопок' %}
                                                            --card-mod-icon-color: cyan;
                                                            {% else %}
                                                            --card-mod-icon-color: grey;
                                                            {% endif %}
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
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set program = states('sensor.bianca_program') %}
                                                            {% if program == 'Синтетика и цветные ткани' %}
                                                            --card-mod-icon-color: cyan;
                                                            {% else %}
                                                            --card-mod-icon-color: grey;
                                                            {% endif %}
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
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set program = states('sensor.bianca_program') %}
                                                            {% if program == 'Шерсть' %}
                                                            --card-mod-icon-color: cyan;
                                                            {% else %}
                                                            --card-mod-icon-color: grey;
                                                            {% endif %}
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
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set program = states('sensor.bianca_program') %}
                                                            {% if program == 'Деликатная' %}
                                                            --card-mod-icon-color: cyan;
                                                            {% else %}
                                                            --card-mod-icon-color: grey;
                                                            {% endif %}
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
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set program = states('sensor.bianca_program') %}
                                                            {% if program == 'Perfect 20°C' %}
                                                            --card-mod-icon-color: cyan;
                                                            {% else %}
                                                            --card-mod-icon-color: grey;
                                                            {% endif %}
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
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set program = states('sensor.bianca_program') %}
                                                            {% if program == 'Полоскание' %}
                                                            --card-mod-icon-color: cyan;
                                                            {% else %}
                                                            --card-mod-icon-color: grey;
                                                            {% endif %}
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
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set program = states('sensor.bianca_program') %}
                                                            {% if program == 'Слив + Отжим' %}
                                                            --card-mod-icon-color: cyan;
                                                            {% else %}
                                                            --card-mod-icon-color: grey;
                                                            {% endif %}
                                                        {% else %}
                                                            --card-mod-icon-color: grey;
                                                        {% endif %}
                                                        pointer-events: none;
                                                    }
                                                `
                                            }
                                        },
                                        // ========== МАЛЕНЬКАЯ ИКОНКА ВРЕМЕНИ ПЕРЕД ЗНАЧЕНИЕМ ==========
                                        {
                                            type: "icon",
                                            icon: "mdi:timer-play-outline",
                                            style: { 
                                                left: "27%", 
                                                top: "34.5%", 
                                                "--mdc-icon-size": "26px",
                                                "transform": "translate(0%, 0%)",
                                                "color": "aqua"
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                                   and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% if machine_ready %}
                                                            visibility: hidden;
                                                            {% else %}
                                                            visibility: visible;
                                                            {% endif %}
                                                        {% else %}
                                                            visibility: hidden;
                                                        {% endif %}
                                                        pointer-events: none;
                                                    }
                                                `
                                            }
                                        },
                                        // ========== МАЛЕНЬКАЯ ИКОНКА ОТЖИМА ПЕРЕД ЗНАЧЕНИЕМ ==========
                                        {
                                            type: "icon",
                                            icon: "mdi:rotate-right",
                                            style: { 
                                                left: "58%", 
                                                top: "34.5%", 
                                                "--mdc-icon-size": "26px",
                                                "transform": "translate(0%, 0%)",
                                                "color": "aqua"
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                                   and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% if machine_ready %}
                                                            visibility: hidden;
                                                            {% else %}
                                                            visibility: visible;
                                                            {% endif %}
                                                        {% else %}
                                                            visibility: hidden;
                                                        {% endif %}
                                                        pointer-events: none;
                                                    }
                                                `
                                            }
                                        },
                                        // ========== МАЛЕНЬКАЯ ИКОНКА ТЕМПЕРАТУРЫ ПЕРЕД ЗНАЧЕНИЕМ ==========
                                        {
                                            type: "icon",
                                            icon: "mdi:thermometer-water",
                                            style: { 
                                                left: "62%", 
                                                top: "38.5%", 
                                                "--mdc-icon-size": "26px",
                                                "transform": "translate(0%, 0%)",
                                                "color": "aqua"
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                                   and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% if machine_ready %}
                                                            visibility: hidden;
                                                            {% else %}
                                                            visibility: visible;
                                                            {% endif %}
                                                        {% else %}
                                                            visibility: hidden;
                                                        {% endif %}
                                                        pointer-events: none;
                                                    }
                                                `
                                            }
                                        },
                                        // ========== ОТЖИМ (РАБОЧИЙ) ==========
                                        {
                                            type: "state-label",
                                            entity: "sensor.bianca_spin_speed",
                                            style: { 
                                                left: "62%", 
                                                top: "33%", 
                                                "font-size": "18px", 
                                                "font-weight": "bold", 
                                                color: "aqua",
                                                "transform": "translate(0%, 0%)"
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                                   and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% if machine_ready %}
                                                            visibility: hidden;
                                                            {% else %}
                                                            visibility: visible;
                                                            {% endif %}
                                                        {% else %}
                                                            visibility: hidden;
                                                        {% endif %}
                                                        pointer-events: none;
                                                    }
                                                `
                                            }
                                        },
                                        // ========== ТЕМПЕРАТУРА (РАБОЧАЯ) ==========
                                        {
                                            type: "state-label",
                                            entity: "sensor.bianca_temperature",
                                            style: { 
                                                left: "66.5%", 
                                                top: "37.5%", 
                                                "font-size": "18px", 
                                                "font-weight": "bold", 
                                                color: "cyan",
                                                "transform": "translate(0%, 0%)"
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                                   and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% if machine_ready %}
                                                            visibility: hidden;
                                                            {% else %}
                                                            visibility: visible;
                                                            {% endif %}
                                                        {% else %}
                                                            visibility: hidden;
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
                                                "font-size": "18px", 
                                                "font-weight": "bold", 
                                                color: "cyan",
                                                "transform": "translate(0%, 0%)"
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                                   and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% if machine_ready %}
                                                            visibility: visible;
                                                            {% else %}
                                                            visibility: hidden;
                                                            {% endif %}
                                                        {% else %}
                                                            visibility: hidden;
                                                        {% endif %}
                                                        pointer-events: none;
                                                    }
                                                `
                                            }
                                        },
                                        // ========== ИКОНКА ТЕМПЕРАТУРЫ (УПРАВЛЕНИЕ) ==========
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
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                                   and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% if machine_ready %}
                                                            --card-mod-icon-color: cyan;
                                                            pointer-events: auto;
                                                            {% else %}
                                                            --card-mod-icon-color: grey;
                                                            pointer-events: none;
                                                            {% endif %}
                                                        {% else %}
                                                            --card-mod-icon-color: grey;
                                                            pointer-events: none;
                                                        {% endif %}
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
                                                "font-size": "18px", 
                                                "font-weight": "bold", 
                                                color: "cyan",
                                                "transform": "translate(0%, 0%)"
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                                   and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% if machine_ready %}
                                                            visibility: visible;
                                                            {% else %}
                                                            visibility: hidden;
                                                            {% endif %}
                                                        {% else %}
                                                            visibility: hidden;
                                                        {% endif %}
                                                        pointer-events: none;
                                                    }
                                                `
                                            }
                                        },
                                        // ========== ИКОНКА ОТЖИМА (УПРАВЛЕНИЕ) ==========
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
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                                   and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% if machine_ready %}
                                                            --card-mod-icon-color: cyan;
                                                            pointer-events: auto;
                                                            {% else %}
                                                            --card-mod-icon-color: grey;
                                                            pointer-events: none;
                                                            {% endif %}
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
                                                "font-size": "18px", 
                                                "font-weight": "bold", 
                                                color: "cyan",
                                                "transform": "translate(0%, 0%)"
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                                   and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% if machine_ready %}
                                                            visibility: hidden;
                                                            {% else %}
                                                            visibility: visible;
                                                            {% endif %}
                                                        {% else %}
                                                            visibility: hidden;
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
                                                "font-size": "18px", 
                                                "font-weight": "bold", 
                                                color: "cyan",
                                                "transform": "translate(0%, 0%)"
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                                   and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% if machine_ready %}
                                                            visibility: visible;
                                                            {% else %}
                                                            visibility: hidden;
                                                            {% endif %}
                                                        {% else %}
                                                            visibility: hidden;
                                                        {% endif %}
                                                        pointer-events: none;
                                                    }
                                                `
                                            }
                                        },
                                        // ========== ИКОНКА ЗАДЕРЖКИ (УПРАВЛЕНИЕ) ==========
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
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                                   and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% if machine_ready %}
                                                            --card-mod-icon-color: cyan;
                                                            pointer-events: auto;
                                                            {% else %}
                                                            --card-mod-icon-color: grey;
                                                            pointer-events: none;
                                                            {% endif %}
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
                                                "font-size": "18px", 
                                                "font-weight": "bold", 
                                                color: "cyan",
                                                "transform": "translate(0%, 0%)"
                                            },
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                                   and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% if machine_ready %}
                                                            visibility: hidden;
                                                            {% else %}
                                                            visibility: visible;
                                                            {% endif %}
                                                        {% else %}
                                                            visibility: hidden;
                                                        {% endif %}
                                                        pointer-events: none;
                                                    }
                                                `
                                            }
                                        },
                                        // ========== ИКОНКА ПАРА (ВСЕГДА ВИДИМА) ==========
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
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                                   and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% if machine_ready %}
                                                                {% set steam_val = states('select.bianca_steam') %}
                                                            {% else %}
                                                                {% set steam_val = states('sensor.bianca_steam') %}
                                                            {% endif %}
                                                            visibility: visible;
                                                            {% if machine_ready %}
                                                            pointer-events: auto;
                                                            --card-mod-icon-color: {{ 'cyan' if steam_val == 'С паром' else 'grey' }};
                                                            {% else %}
                                                            pointer-events: none;
                                                            --card-mod-icon-color: {{ 'cyan' if steam_val == 'Включен' else 'grey' }};
                                                            {% endif %}
                                                        {% else %}
                                                            --card-mod-icon-color: grey;
                                                            pointer-events: none;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        },
                                        // ========== ИКОНКА УРОВНЯ ЗАГРЯЗНЕНИЯ (СКРЫВАЕМ ПРИ "Нет") ==========
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
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                                   and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% set program = states('sensor.bianca_program') %}
                                                            
                                                            {% if machine_ready %}
                                                                {% set soil_val = states('select.bianca_soil') %}
                                                            {% else %}
                                                                {% set soil_val = states('sensor.bianca_soil_level') %}
                                                            {% endif %}
                                                            
                                                            {% if soil_val in ['Мало', 'Нормально', 'Очень'] %}
                                                                {% if program == 'Perfect 20°C' %}
                                                                --card-mod-icon: phu:duco-2;
                                                                --card-mod-icon-color: cyan;
                                                                pointer-events: none;
                                                                
                                                                {% elif program in ['Шерсть', 'Деликатная', 'Полоскание', 'Слив + Отжим', 'Сохранить свежесть', 'Perfect rapid 59 минут'] %}
                                                                --card-mod-icon: phu:duco-1;
                                                                --card-mod-icon-color: grey;
                                                                pointer-events: none;
                                                                
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
                                                                visibility: visible;
                                                            {% else %}
                                                                visibility: hidden;
                                                            {% endif %}
                                                        {% else %}
                                                            visibility: hidden;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        },
                                        // ========== ИКОНКА ПРЕДВАРИТЕЛЬНОЙ СТИРКИ (СКРЫВАЕМ ПРИ "Нет") ==========
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
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                                   and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% if machine_ready %}
                                                                {% set prewash_val = states('select.bianca_pre_wash') %}
                                                            {% else %}
                                                                {% set prewash_val = states('sensor.bianca_pre_wash') %}
                                                            {% endif %}
                                                            
                                                            {% if prewash_val in ['Есть', 'Включен'] %}
                                                            visibility: visible;
                                                            {% if machine_ready %}
                                                            pointer-events: auto;
                                                            --card-mod-icon-color: cyan;
                                                            {% else %}
                                                            pointer-events: none;
                                                            --card-mod-icon-color: cyan;
                                                            {% endif %}
                                                            {% else %}
                                                            visibility: hidden;
                                                            {% endif %}
                                                        {% else %}
                                                            visibility: hidden;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        },
                                        // ========== ИКОНКА ГИГИЕНЫ (СКРЫВАЕМ ПРИ "Выключен") ==========
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
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                                   and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% if machine_ready %}
                                                                {% set hygiene_val = states('select.bianca_hygiene') %}
                                                            {% else %}
                                                                {% set hygiene_val = states('sensor.bianca_hygienic_wash') %}
                                                            {% endif %}
                                                            
                                                            {% if hygiene_val in ['Есть', 'Включен'] %}
                                                            visibility: visible;
                                                            {% if machine_ready %}
                                                            pointer-events: auto;
                                                            --card-mod-icon-color: cyan;
                                                            {% else %}
                                                            pointer-events: none;
                                                            --card-mod-icon-color: cyan;
                                                            {% endif %}
                                                            {% else %}
                                                            visibility: hidden;
                                                            {% endif %}
                                                        {% else %}
                                                            visibility: hidden;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        },
                                        // ========== ИКОНКА АНТИСМИНАНИЯ (СКРЫВАЕМ ПРИ "Выключен") ==========
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
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                                   and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% if machine_ready %}
                                                                {% set anticrease_val = states('select.bianca_anti_crease') %}
                                                            {% else %}
                                                                {% set anticrease_val = states('sensor.bianca_anti_crease') %}
                                                            {% endif %}
                                                            
                                                            {% if anticrease_val in ['Есть', 'Включен'] %}
                                                            visibility: visible;
                                                            {% if machine_ready %}
                                                            pointer-events: auto;
                                                            --card-mod-icon-color: cyan;
                                                            {% else %}
                                                            pointer-events: none;
                                                            --card-mod-icon-color: cyan;
                                                            {% endif %}
                                                            {% else %}
                                                            visibility: hidden;
                                                            {% endif %}
                                                        {% else %}
                                                            visibility: hidden;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        },
                                        // ========== ИКОНКА НОЧНОЙ СТИРКИ (СКРЫВАЕМ ПРИ "Выключен") ==========
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
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                                   and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% if machine_ready %}
                                                                {% set nightspin_val = states('select.bianca_night_spin') %}
                                                            {% else %}
                                                                {% set nightspin_val = states('sensor.bianca_night_spin') %}
                                                            {% endif %}
                                                            
                                                            {% if nightspin_val in ['Есть', 'Включен'] %}
                                                            visibility: visible;
                                                            {% if machine_ready %}
                                                            pointer-events: auto;
                                                            --card-mod-icon-color: cyan;
                                                            {% else %}
                                                            pointer-events: none;
                                                            --card-mod-icon-color: cyan;
                                                            {% endif %}
                                                            {% else %}
                                                            visibility: hidden;
                                                            {% endif %}
                                                        {% else %}
                                                            visibility: hidden;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        },
                                        // ========== ИКОНКА ДОПОЛНИТЕЛЬНЫХ ПОЛОСКАНИЙ (СКРЫВАЕМ ПРИ "Нет") ==========
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
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                                   and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% if machine_ready %}
                                                                {% set rinse_val = states('select.bianca_extra_rinse') %}
                                                            {% else %}
                                                                {# No direct sensor for rinse count #}
                                                                {% set rinse_val = 'Нет' %}
                                                            {% endif %}
                                                            
                                                            {% if rinse_val in ['1 полоскание', '2 полоскания', '3 полоскания'] %}
                                                            visibility: visible;
                                                            {% if machine_ready %}
                                                            pointer-events: auto;
                                                            {% if rinse_val == '1 полоскание' %}
                                                            --card-mod-icon-color: cyan;
                                                            {% elif rinse_val == '2 полоскания' %}
                                                            --card-mod-icon: bianca:rinse-2;
                                                            --card-mod-icon-color: cyan;
                                                            {% elif rinse_val == '3 полоскания' %}
                                                            --card-mod-icon: bianca:rinse-3;
                                                            --card-mod-icon-color: cyan;
                                                            {% endif %}
                                                            {% else %}
                                                            pointer-events: none;
                                                            --card-mod-icon-color: cyan;
                                                            {% endif %}
                                                            {% else %}
                                                            visibility: hidden;
                                                            {% endif %}
                                                        {% else %}
                                                            visibility: hidden;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        },
                                        // ========== ИКОНКА АКВАПЛЮС (СКРЫВАЕМ ПРИ "Выключен") ==========
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
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                                   and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% if machine_ready %}
                                                                {% set aquaplus_val = states('select.bianca_aqua_plus') %}
                                                            {% else %}
                                                                {% set aquaplus_val = states('sensor.bianca_aqua_plus') %}
                                                            {% endif %}
                                                            
                                                            {% if aquaplus_val in ['Есть', 'Включен'] %}
                                                            visibility: visible;
                                                            {% if machine_ready %}
                                                            pointer-events: auto;
                                                            --card-mod-icon-color: cyan;
                                                            {% else %}
                                                            pointer-events: none;
                                                            --card-mod-icon-color: cyan;
                                                            {% endif %}
                                                            {% else %}
                                                            visibility: hidden;
                                                            {% endif %}
                                                        {% else %}
                                                            visibility: hidden;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        },
                                        // ========== ИКОНКА ZOOM (ВСЕГДА ВИДИМА) ==========
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
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                                   and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% if machine_ready %}
                                                                {% set zoom_val = states('select.bianca_zoom') %}
                                                            {% else %}
                                                                {% set zoom_val = states('sensor.bianca_zoom') %}
                                                            {% endif %}
                                                            visibility: visible;
                                                            {% if machine_ready %}
                                                            pointer-events: auto;
                                                            --card-mod-icon-color: {{ 'cyan' if zoom_val == 'Есть' else 'grey' }};
                                                            {% else %}
                                                            pointer-events: none;
                                                            --card-mod-icon-color: {{ 'cyan' if zoom_val == 'Включен' else 'grey' }};
                                                            {% endif %}
                                                        {% else %}
                                                            --card-mod-icon-color: grey;
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
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                                   and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% if machine_ready %}
                                                            pointer-events: auto;
                                                            --card-mod-icon-color: white;
                                                            {% else %}
                                                            pointer-events: none;
                                                            --card-mod-icon-color: grey;
                                                            {% endif %}
                                                        {% else %}
                                                            --card-mod-icon-color: grey;
                                                            pointer-events: none;
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
                                                        {% if is_state('binary_sensor.bianca_available', 'on') and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') %}
                                                            {% if not machine_ready %}
                                                            pointer-events: auto;
                                                            --card-mod-icon-color: white;
                                                            {% else %}
                                                            pointer-events: none;
                                                            --card-mod-icon-color: grey;
                                                            {% endif %}
                                                        {% else %}
                                                            --card-mod-icon-color: grey;
                                                            pointer-events: none;
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
                                    ],
                                    card_mod: {
                                        style: `
                                            :host {
                                                {% if not is_state('binary_sensor.bianca_available', 'on') %}
                                                display: none;
                                                {% endif %}
                                            }
                                        `
                                    }
                                },
                                // ========== КАРТОЧКА ПАРАМЕТРОВ ==========
                                {
                                    type: "entities",
                                    title: "Параметры",
                                    state_color: true,
                                    entities: [
                                        {
                                            entity: "select.bianca_program",
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                                   and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% if not machine_ready %}
                                                            opacity: 0.6;
                                                            pointer-events: none;
                                                            {% endif %}
                                                        {% else %}
                                                            visibility: hidden;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            entity: "select.bianca_temperature",
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                                   and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% if not machine_ready %}
                                                            opacity: 0.6;
                                                            pointer-events: none;
                                                            {% endif %}
                                                        {% else %}
                                                            visibility: hidden;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            entity: "select.bianca_spin",
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                                   and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% if not machine_ready %}
                                                            opacity: 0.6;
                                                            pointer-events: none;
                                                            {% endif %}
                                                        {% else %}
                                                            visibility: hidden;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            entity: "select.bianca_delay_start",
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                                   and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% if not machine_ready %}
                                                            opacity: 0.6;
                                                            pointer-events: none;
                                                            {% endif %}
                                                        {% else %}
                                                            visibility: hidden;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            entity: "select.bianca_soil",
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                                   and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% if not machine_ready %}
                                                            opacity: 0.6;
                                                            pointer-events: none;
                                                            {% endif %}
                                                        {% else %}
                                                            visibility: hidden;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            entity: "select.bianca_steam",
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                                   and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% if not machine_ready %}
                                                            opacity: 0.6;
                                                            pointer-events: none;
                                                            {% endif %}
                                                        {% else %}
                                                            visibility: hidden;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            entity: "select.bianca_pre_wash",
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                                   and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% if not machine_ready %}
                                                            opacity: 0.6;
                                                            pointer-events: none;
                                                            {% endif %}
                                                        {% else %}
                                                            visibility: hidden;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            entity: "select.bianca_hygiene",
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                                   and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% if not machine_ready %}
                                                            opacity: 0.6;
                                                            pointer-events: none;
                                                            {% endif %}
                                                        {% else %}
                                                            visibility: hidden;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            entity: "select.bianca_anti_crease",
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                                   and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% if not machine_ready %}
                                                            opacity: 0.6;
                                                            pointer-events: none;
                                                            {% endif %}
                                                        {% else %}
                                                            visibility: hidden;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            entity: "select.bianca_night_spin",
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                                   and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% if not machine_ready %}
                                                            opacity: 0.6;
                                                            pointer-events: none;
                                                            {% endif %}
                                                        {% else %}
                                                            visibility: hidden;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            entity: "select.bianca_extra_rinse",
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                                   and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% if not machine_ready %}
                                                            opacity: 0.6;
                                                            pointer-events: none;
                                                            {% endif %}
                                                        {% else %}
                                                            visibility: hidden;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            entity: "select.bianca_aqua_plus",
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                                   and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% if not machine_ready %}
                                                            opacity: 0.6;
                                                            pointer-events: none;
                                                            {% endif %}
                                                        {% else %}
                                                            visibility: hidden;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            entity: "select.bianca_zoom",
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if is_state('binary_sensor.bianca_available', 'on') %}
                                                            {% set machine_ready = is_state('sensor.bianca_machine_state', 'Бездействие') 
                                                                   and is_state('sensor.bianca_remote_control', 'Вкл') %}
                                                            {% if not machine_ready %}
                                                            opacity: 0.6;
                                                            pointer-events: none;
                                                            {% endif %}
                                                        {% else %}
                                                            visibility: hidden;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        }
                                    ],
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
