// BIANCA SIMPLE DASHBOARD STRATEGY - Version 2.4.3
// FIX: Добавлена блокировка селектов при недоступности машины (2026-06-07)
console.log("Loading bianca-simple.js");

// ========== МГНОВЕННАЯ БЛОКИРОВКА КНОПОК ==========
(function() {
    function getButtonByName(name) {
        const buttons = document.querySelectorAll('button');
        for (const btn of buttons) {
            const nameEl = btn.querySelector('.name');
            if (nameEl && nameEl.textContent === name) {
                return btn;
            }
        }
        return null;
    }
    
    function disableButton(btn, disabled) {
        if (!btn) return;
        if (disabled) {
            btn.setAttribute('disabled', 'disabled');
            btn.style.opacity = '0.5';
            btn.style.pointerEvents = 'none';
        } else {
            btn.removeAttribute('disabled');
            btn.style.opacity = '1';
            btn.style.pointerEvents = 'auto';
        }
    }
    
    function updateButtonsState() {
        const startBtn = getButtonByName('СТАРТ');
        const stopBtn = getButtonByName('СТОП');
        
        const available = document.querySelector('binary_sensor.bianca_available')?.getAttribute('state') === 'on';
        const remoteControl = document.querySelector('sensor.bianca_remote_control')?.getAttribute('state') === 'Вкл';
        const machineState = document.querySelector('sensor.bianca_machine_state')?.getAttribute('state');
        const isIdle = machineState === 'Бездействие';
        
        const startEnabled = available && remoteControl && isIdle;
        const stopEnabled = available && remoteControl && !isIdle;
        
        disableButton(startBtn, !startEnabled);
        disableButton(stopBtn, !stopEnabled);
    }
    
    function handleStartClick() {
        const startBtn = getButtonByName('СТАРТ');
        const stopBtn = getButtonByName('СТОП');
        
        // Мгновенно блокируем СТАРТ, разблокируем СТОП
        disableButton(startBtn, true);
        disableButton(stopBtn, false);
        
        // Через 5 секунд обновим состояние
        setTimeout(updateButtonsState, 5000);
    }
    
    function handleStopClick() {
        const startBtn = getButtonByName('СТАРТ');
        const stopBtn = getButtonByName('СТОП');
        
        // Мгновенно блокируем СТОП, разблокируем СТАРТ
        disableButton(startBtn, false);
        disableButton(stopBtn, true);
        
        // Через 5 секунд обновим состояние
        setTimeout(updateButtonsState, 5000);
    }
    
    function init() {
        updateButtonsState();
        
        const startBtn = getButtonByName('СТАРТ');
        const stopBtn = getButtonByName('СТОП');
        
        if (startBtn) {
            startBtn.removeEventListener('click', handleStartClick);
            startBtn.addEventListener('click', handleStartClick);
        }
        if (stopBtn) {
            stopBtn.removeEventListener('click', handleStopClick);
            stopBtn.addEventListener('click', handleStopClick);
        }
        
        // Следим за изменениями состояний
        const observer = new MutationObserver(() => {
            updateButtonsState();
        });
        observer.observe(document.body, { childList: true, subtree: true, attributes: true, attributeFilter: ['state'] });
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();

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
                                                style: `
                                                    ha-card {
                                                        background: #4CAF50;
                                                        color: white;
                                                        border-radius: 28px;
                                                        text-align: center;
                                                        padding: 12px;
                                                    }
                                                    .name {
                                                        font-weight: bold;
                                                        font-size: 16px;
                                                        color: white;
                                                    }
                                                    .icon {
                                                        --mdc-icon-size: 32px;
                                                        color: white;
                                                    }
                                                `
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
                                                style: `
                                                    ha-card {
                                                        background: #F44336;
                                                        color: white;
                                                        border-radius: 28px;
                                                        text-align: center;
                                                        padding: 12px;
                                                    }
                                                    .name {
                                                        font-weight: bold;
                                                        font-size: 16px;
                                                        color: white;
                                                    }
                                                    .icon {
                                                        --mdc-icon-size: 32px;
                                                        color: white;
                                                    }
                                                `
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
                                    entities: [
                                        {
                                            entity: "select.bianca_program",
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if not (is_state('binary_sensor.bianca_available', 'on') 
                                                            and is_state('sensor.bianca_machine_state', 'Бездействие')
                                                            and is_state('sensor.bianca_remote_control', 'Вкл')) %}
                                                        opacity: 0.6;
                                                        pointer-events: none;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        }
                                    ],
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
                                            state_color: true,
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if not (is_state('binary_sensor.bianca_available', 'on') 
                                                            and is_state('sensor.bianca_machine_state', 'Бездействие')
                                                            and is_state('sensor.bianca_remote_control', 'Вкл')) %}
                                                        opacity: 0.6;
                                                        pointer-events: none;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        },
                                        {
                                            type: "entity",
                                            entity: "select.bianca_spin",
                                            name: " ",
                                            state_color: true,
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if not (is_state('binary_sensor.bianca_available', 'on') 
                                                            and is_state('sensor.bianca_machine_state', 'Бездействие')
                                                            and is_state('sensor.bianca_remote_control', 'Вкл')) %}
                                                        opacity: 0.6;
                                                        pointer-events: none;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        }
                                    ]
                                },
                                {
                                    type: "horizontal-stack",
                                    cards: [
                                        {
                                            type: "entity",
                                            entity: "sensor.bianca_delay_start",
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
                                    entities: [
                                        { 
                                            entity: "select.bianca_temperature",
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if not (is_state('binary_sensor.bianca_available', 'on') 
                                                            and is_state('sensor.bianca_machine_state', 'Бездействие')
                                                            and is_state('sensor.bianca_remote_control', 'Вкл')) %}
                                                        opacity: 0.6;
                                                        pointer-events: none;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        }
                                    ],
                                    state_color: false
                                },
                                {
                                    type: "entities",
                                    show_header_toggle: false,
                                    entities: [
                                        { 
                                            entity: "select.bianca_spin",
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if not (is_state('binary_sensor.bianca_available', 'on') 
                                                            and is_state('sensor.bianca_machine_state', 'Бездействие')
                                                            and is_state('sensor.bianca_remote_control', 'Вкл')) %}
                                                        opacity: 0.6;
                                                        pointer-events: none;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        }
                                    ],
                                    state_color: false
                                },
                                {
                                    type: "entities",
                                    show_header_toggle: false,
                                    entities: [
                                        { 
                                            entity: "select.bianca_steam",
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if not (is_state('binary_sensor.bianca_available', 'on') 
                                                            and is_state('sensor.bianca_machine_state', 'Бездействие')
                                                            and is_state('sensor.bianca_remote_control', 'Вкл')) %}
                                                        opacity: 0.6;
                                                        pointer-events: none;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        }
                                    ],
                                    state_color: false
                                },
                                {
                                    type: "entities",
                                    show_header_toggle: false,
                                    entities: [
                                        { 
                                            entity: "select.bianca_zoom",
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if not (is_state('binary_sensor.bianca_available', 'on') 
                                                            and is_state('sensor.bianca_machine_state', 'Бездействие')
                                                            and is_state('sensor.bianca_remote_control', 'Вкл')) %}
                                                        opacity: 0.6;
                                                        pointer-events: none;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        }
                                    ],
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
                                    entities: [
                                        { 
                                            entity: "select.bianca_delay_start",
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if not (is_state('binary_sensor.bianca_available', 'on') 
                                                            and is_state('sensor.bianca_machine_state', 'Бездействие')
                                                            and is_state('sensor.bianca_remote_control', 'Вкл')) %}
                                                        opacity: 0.6;
                                                        pointer-events: none;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        }
                                    ],
                                    state_color: false
                                },
                                {
                                    type: "entities",
                                    show_header_toggle: false,
                                    entities: [
                                        { 
                                            entity: "select.bianca_hygiene",
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if not (is_state('binary_sensor.bianca_available', 'on') 
                                                            and is_state('sensor.bianca_machine_state', 'Бездействие')
                                                            and is_state('sensor.bianca_remote_control', 'Вкл')) %}
                                                        opacity: 0.6;
                                                        pointer-events: none;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        }
                                    ],
                                    state_color: false
                                },
                                {
                                    type: "entities",
                                    show_header_toggle: false,
                                    entities: [
                                        { 
                                            entity: "select.bianca_soil",
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if not (is_state('binary_sensor.bianca_available', 'on') 
                                                            and is_state('sensor.bianca_machine_state', 'Бездействие')
                                                            and is_state('sensor.bianca_remote_control', 'Вкл')) %}
                                                        opacity: 0.6;
                                                        pointer-events: none;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        }
                                    ],
                                    state_color: false
                                },
                                {
                                    type: "entities",
                                    show_header_toggle: false,
                                    entities: [
                                        { 
                                            entity: "select.bianca_anti_crease",
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if not (is_state('binary_sensor.bianca_available', 'on') 
                                                            and is_state('sensor.bianca_machine_state', 'Бездействие')
                                                            and is_state('sensor.bianca_remote_control', 'Вкл')) %}
                                                        opacity: 0.6;
                                                        pointer-events: none;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        }
                                    ],
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
                                    entities: [
                                        { 
                                            entity: "select.bianca_pre_wash",
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if not (is_state('binary_sensor.bianca_available', 'on') 
                                                            and is_state('sensor.bianca_machine_state', 'Бездействие')
                                                            and is_state('sensor.bianca_remote_control', 'Вкл')) %}
                                                        opacity: 0.6;
                                                        pointer-events: none;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        }
                                    ],
                                    state_color: false
                                },
                                {
                                    type: "entities",
                                    show_header_toggle: false,
                                    entities: [
                                        { 
                                            entity: "select.bianca_aqua_plus",
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if not (is_state('binary_sensor.bianca_available', 'on') 
                                                            and is_state('sensor.bianca_machine_state', 'Бездействие')
                                                            and is_state('sensor.bianca_remote_control', 'Вкл')) %}
                                                        opacity: 0.6;
                                                        pointer-events: none;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        }
                                    ],
                                    state_color: false
                                },
                                {
                                    type: "entities",
                                    show_header_toggle: false,
                                    entities: [
                                        { 
                                            entity: "select.bianca_night_spin",
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if not (is_state('binary_sensor.bianca_available', 'on') 
                                                            and is_state('sensor.bianca_machine_state', 'Бездействие')
                                                            and is_state('sensor.bianca_remote_control', 'Вкл')) %}
                                                        opacity: 0.6;
                                                        pointer-events: none;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        }
                                    ],
                                    state_color: false
                                },
                                {
                                    type: "entities",
                                    show_header_toggle: false,
                                    entities: [
                                        { 
                                            entity: "select.bianca_extra_rinse",
                                            card_mod: {
                                                style: `
                                                    :host {
                                                        {% if not (is_state('binary_sensor.bianca_available', 'on') 
                                                            and is_state('sensor.bianca_machine_state', 'Бездействие')
                                                            and is_state('sensor.bianca_remote_control', 'Вкл')) %}
                                                        opacity: 0.6;
                                                        pointer-events: none;
                                                        {% endif %}
                                                    }
                                                `
                                            }
                                        }
                                    ],
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
