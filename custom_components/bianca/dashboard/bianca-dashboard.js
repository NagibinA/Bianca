class BiancaDashboardStrategy {
  async generate() {
    return {
      title: "Bianca",
      views: [
        {
          title: "Главная",
          cards: [
            {
              type: "entities",
              entities: [
                "binary_sensor.bianca_available",
                "sensor.bianca_machine_state",
                "sensor.bianca_program",
                "sensor.bianca_temperature",
                "sensor.bianca_spin_speed"
              ]
            }
          ]
        }
      ]
    };
  }
}

window.customStrategies = window.customStrategies || [];
window.customStrategies.push({
  type: "bianca",
  name: "Bianca",
  description: "Управление стиральной машиной Bianca",
  generate: (config, hass, resources, view) => {
    return new BiancaDashboardStrategy().generate(config, hass, resources, view);
  }
});
