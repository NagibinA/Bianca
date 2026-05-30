// Dashboard strategy for Bianca washing machine
class BiancaDashboardStrategy {
  static async generate(config, hass, resources, view) {
    // Получаем IP устройства из конфига или используем переменную
    // В реальной интеграции нужно будет передавать IP из настроек
    
    // Строим структуру дашборда с картинкой-фоном и наложенными элементами
    const dashboard = {
      title: config.title || "Bianca",
      views: [
        {
          title: "Управление",
          type: "sections",
          sections: [
            {
              type: "grid",
              cards: [
                // Основная карточка с изображением машины и элементами управления
                {
                  type: "picture-elements",
                  image: "/local/community/bianca/original.png",
                  elements: [
                    // Кнопка питания (иконка)
                    {
                      type: "icon",
                      icon: "mdi:power",
                      style: {
                        left: "44%",
                        top: "11%",
                        "--mdc-icon-size": "49px"
                      },
                      tap_action: {
                        action: "none"
                      }
                    },
                    // Иконка температуры (слева внизу)
                    {
                      type: "icon",
                      icon: "mdi:thermometer-water",
                      style: {
                        left: "20%",
                        top: "50%",
                        "--mdc-icon-size": "49px"
                      },
                      tap_action: {
                        action: "none"
                      }
                    },
                    // Иконка отжима
                    {
                      type: "icon",
                      icon: "mdi:rotate-right",
                      style: {
                        left: "11.5%",
                        top: "40.5%",
                        "--mdc-icon-size": "49px"
                      },
                      tap_action: {
                        action: "none"
                      }
                    },
                    // Иконка отложенного старта
                    {
                      type: "icon",
                      icon: "mdi:timer-outline",
                      style: {
                        left: "11%",
                        top: "30%",
                        "--mdc-icon-size": "49px"
                      },
                      tap_action: {
                        action: "none"
                      }
                    },
                    // Значение температуры
                    {
                      type: "state-label",
                      entity: "sensor.bianca_temperature",
                      style: {
                        left: "27%",
                        top: "51%",
                        fontSize: "18px",
                        fontWeight: "bold"
                      }
                    },
                    // Значение оборотов отжима
                    {
                      type: "state-label",
                      entity: "sensor.bianca_spin_speed",
                      style: {
                        left: "20%",
                        top: "41%",
                        fontSize: "18px",
                        fontWeight: "bold"
                      }
                    },
                    // Оставшееся время
                    {
                      type: "state-label",
                      entity: "sensor.bianca_remaining_time",
                      style: {
                        left: "27%",
                        top: "34%",
                        fontSize: "18px",
                        fontWeight: "bold",
                        color: "cyan"
                      }
                    },
                    // Фаза программы
                    {
                      type: "state-label",
                      entity: "sensor.bianca_program_phase",
                      style: {
                        left: "27%",
                        top: "39%",
                        fontSize: "16px",
                        fontWeight: "bold"
                      }
                    },
                    // Текущая программа (по центру)
                    {
                      type: "state-label",
                      entity: "sensor.bianca_program",
                      style: {
                        left: "50%",
                        top: "49%",
                        fontSize: "14px",
                        textAlign: "center",
                        width: "40%"
                      }
                    }
                  ]
                },
                // Карточка со всеми сенсорами в виде списка
                {
                  type: "entities",
                  title: "Состояние",
                  entities: [
                    {
                      entity: "binary_sensor.bianca_ping",
                      name: "Доступность",
                      icon: "mdi:network"
                    },
                    {
                      entity: "sensor.bianca_api_response",
                      name: "Статус API",
                      icon: "mdi:api"
                    },
                    "sensor.bianca_machine_state",
                    "sensor.bianca_program",
                    "sensor.bianca_program_phase",
                    "sensor.bianca_remaining_time",
                    "sensor.bianca_temperature",
                    "sensor.bianca_spin_speed"
                  ]
                },
                // Карточка с опциями
                {
                  type: "entities",
                  title: "Опции",
                  entities: [
                    "sensor.bianca_steam",
                    "sensor.bianca_pre_wash",
                    "sensor.bianca_hygienic_wash",
                    "sensor.bianca_anti_crease",
                    "sensor.bianca_night_spin",
                    "sensor.bianca_aqua_plus",
                    "sensor.bianca_zoom"
                  ]
                }
              ]
            }
          ]
        }
      ]
    };
    
    return dashboard;
  }
}

// Регистрируем стратегию
window.customStrategies = window.customStrategies || [];
window.customStrategies.push({
  type: "bianca",
  strategyType: "dashboard",
  name: "Bianca",
  description: "Управление стиральной машиной Bianca",
  generate: BiancaDashboardStrategy.generate
});
