// Dashboard strategy for Bianca washing machine
class BiancaDashboardStrategy {
  async generate(config, hass, resources, view) {
    const dashboardConfig = {
      title: "Bianca",
      views: [
        {
          title: "Управление",
          path: "bianca-main",
          type: "sections",
          sections: [
            {
              type: "grid",
              cards: [
                {
                  type: "picture",
                  image: "/local/community/bianca/original.png",
                  title: "Стиральная машина Bianca"
                },
                {
                  type: "entities",
                  title: "Состояние",
                  entities: [
                    "binary_sensor.bianca_available",
                    "sensor.bianca_api_response",
                    "sensor.bianca_machine_state",
                    "sensor.bianca_program",
                    "sensor.bianca_program_phase",
                    "sensor.bianca_remaining_time"
                  ]
                },
                {
                  type: "entities",
                  title: "Параметры",
                  entities: [
                    "sensor.bianca_temperature",
                    "sensor.bianca_spin_speed"
                  ]
                },
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
    
    return dashboardConfig;
  }
}

// Регистрация стратегии
if (!window.customStrategies) {
  window.customStrategies = [];
}

window.customStrategies.push({
  type: "bianca",
  name: "Bianca",
  description: "Управление стиральной машиной Bianca",
  generate: (config, hass, resources, view) => {
    const strategy = new BiancaDashboardStrategy();
    return strategy.generate(config, hass, resources, view);
  }
});
