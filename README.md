# Home Assistant OpenAI Energy Management Agent
An intelligent energy management AI agent for Home Assistant, powered by OpenAI models. This custom component specializes in monitoring, analyzing, and optimizing your home's energy consumption patterns through natural language conversations.

Derived from [Extended OpenAI Conversation](https://github.com/jekalmin/extended_openai_conversation) with enhanced focus on energy management and smart home optimization.

## Key Energy Management Features
- **Energy Monitoring**: Real-time tracking and analysis of home energy consumption
- **Smart Device Control**: Intelligent control of energy-consuming devices based on usage patterns
- **Cost Optimization**: Automated recommendations to reduce energy bills
- **Usage Analytics**: Historical energy data analysis with insights and trends
- **Peak Load Management**: Smart scheduling to avoid peak energy costs
- **Solar Integration**: Optimization for homes with solar panels and battery storage
- **Automation Creation**: AI-powered energy-saving automation suggestions
- **Multi-source Data**: Integration with external energy APIs and smart meters

## How it works
The Energy Management Agent uses OpenAI's advanced function calling capabilities to interact with Home Assistant's energy systems, devices, and historical data. It can analyze your energy patterns, control smart devices, and provide actionable insights to optimize your home's energy efficiency.

The AI agent understands energy concepts like peak hours, renewable energy integration, load balancing, and cost optimization, making it your personal energy consultant.

## Installation
1. Install via HACS by adding this repository: `https://github.com/tianzhihe/ha_openai_energy_agent` or by copying `ha_openai_energy_agent` folder into `<config directory>/custom_components`
2. Restart Home Assistant
3. Go to Settings > Devices & Services.
4. In the bottom right corner, select the Add Integration button.
5. Search for "OpenAI Energy Agent" and follow the setup instructions (OpenAI API Key is required).
    - [Generating an API Key](https://www.home-assistant.io/integrations/openai_conversation/#generate-an-api-key)
    - Specify "Base Url" if using OpenAI compatible servers like Azure OpenAI, LocalAI, or other compatible endpoints
6. Go to Settings > [Voice Assistants](https://my.home-assistant.io/redirect/voice_assistants/).
7. Click to edit Assistant (named "Home Assistant" by default).
8. Select "OpenAI Energy Management Agent" from "Conversation agent" tab.
    <details>

    <summary>guide image</summary>
    <img width="500" alt="스크린샷 2023-10-07 오후 6 15 29" src="https://github.com/jekalmin/extended_openai_conversation/assets/2917984/0849d241-0b82-47f6-9956-fdb82d678aca">

    </details>

## Preparation
After installation, expose your energy-related entities from "http://{your-home-assistant}/config/voice-assistants/expose". Focus on exposing:
- Energy sensors (solar panels, battery storage, grid consumption)
- Smart switches and plugs with energy monitoring
- HVAC systems and smart thermostats
- Water heaters and major appliances
- Lighting systems with dimming capabilities

## Energy Management Examples

### 1. Energy Usage Analysis
Ask: *"What's my current energy consumption and how does it compare to yesterday?"*
The agent analyzes real-time consumption data and provides insights with cost comparisons.

### 2. Smart Device Optimization
Ask: *"Turn off all non-essential devices to reduce my energy bill"*
The agent identifies and controls energy-consuming devices based on priority and usage patterns.

### 3. Solar & Battery Management
Ask: *"How much solar energy did I generate today and what's my battery level?"*
Get comprehensive solar production reports and battery storage status with optimization suggestions.

### 4. Peak Hour Management
Ask: *"Schedule my dishwasher and laundry to avoid peak energy costs"*
The agent creates smart automations to run appliances during off-peak hours.

### 5. Energy-Saving Automations
Ask: *"Create an automation to reduce heating when nobody's home"*
Automatically generates energy-efficient automations based on occupancy and schedules.

## Configuration
### Energy Management Options
Configure the AI agent through the Options menu to optimize energy management capabilities:

**Core Settings:**
- `Energy Focus Prompt`: Specialized prompt template optimized for energy management conversations
- `Model Selection`: Choose GPT models best suited for energy analysis (recommended: gpt-4 for complex analysis)
- `Maximum Function Calls`: Limit function calls per conversation to prevent excessive API usage during energy analysis

**Energy-Specific Features:**
- `Attach Username`: Include user context for personalized energy recommendations
- `Energy Functions`: Pre-configured functions for energy monitoring, solar management, and device control
  - Energy statistics retrieval and analysis
  - Smart device control with energy optimization
  - Solar panel and battery management
  - Peak hour scheduling and cost optimization
  - Historical energy data analysis


| Edit Assist                                                                                                                                  | Options                                                                                                                                                                       |
|----------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| <img width="608" alt="1" src="https://github.com/jekalmin/extended_openai_conversation/assets/2917984/bb394cd4-5790-4ac9-9311-dbcab0fcca56"> | <img width="591" alt="스크린샷 2023-10-10 오후 10 53 57" src="https://github.com/jekalmin/extended_openai_conversation/assets/2917984/431e4bc5-87a0-4d7b-8da0-6273f955877f"> |


### Energy Management Functions

#### Built-in Energy Functions
The agent includes specialized functions optimized for energy management:

**Core Energy Functions:**
- `execute_services`: Control energy-consuming devices and systems
  - Smart switches, plugs, and energy monitoring devices
  - HVAC systems and smart thermostats
  - Solar inverters and battery systems
  - Major appliances with smart controls

- `get_energy_statistics`: Retrieve comprehensive energy data
  - Real-time consumption monitoring
  - Historical energy usage patterns
  - Solar production and battery levels
  - Cost analysis and billing information

- `add_energy_automation`: Create energy-saving automations
  - Peak hour scheduling for appliances
  - Occupancy-based HVAC control
  - Solar optimization routines
  - Load balancing automations

**Advanced Energy Functions:**
- `analyze_energy_patterns`: AI-powered energy usage analysis
- `optimize_device_schedules`: Smart scheduling for energy efficiency
- `solar_battery_management`: Comprehensive renewable energy control
- `cost_optimization`: Utility bill reduction strategies

#### Function Types
- `native`: Built-in energy management functions
- `energy_script`: Energy-focused automation sequences
- `energy_template`: Dynamic energy calculations and reporting
- `utility_api`: Integration with utility providers and smart meters
- `weather_energy`: Weather-based energy optimization
- `composite`: Multi-step energy management workflows 

Below is a default configuration of functions.

```yaml
- spec:
    name: execute_services
    description: Use this function to execute service of devices in Home Assistant.
    parameters:
      type: object
      properties:
        list:
          type: array
          items:
            type: object
            properties:
              domain:
                type: string
                description: The domain of the service
              service:
                type: string
                description: The service to be called
              service_data:
                type: object
                description: The service data object to indicate what to control.
                properties:
                  entity_id:
                    type: string
                    description: The entity_id retrieved from available devices. It must start with domain, followed by dot character.
                required:
                - entity_id
            required:
            - domain
            - service
            - service_data
  function:
    type: native
    name: execute_service
```

## Function Usage
This is an example of configuration of functions.

Copy and paste below yaml configuration into "Functions".<br/>
Then you will be able to let OpenAI call your function. 

### 1. template
#### 1-1. Get current weather

For real world example, see [weather](https://github.com/jekalmin/extended_openai_conversation/tree/main/examples/function/weather).<br/>
This is just an example from [OpenAI documentation](https://platform.openai.com/docs/guides/function-calling/common-use-cases)

```yaml
- spec:
    name: get_current_weather
    description: Get the current weather in a given location
    parameters:
      type: object
      properties:
        location:
          type: string
          description: The city and state, e.g. San Francisco, CA
        unit:
          type: string
          enum:
          - celcius
          - farenheit
      required:
      - location
  function:
    type: template
    value_template: The temperature in {{ location }} is 25 {{unit}}
```

<img width="300" alt="스크린샷 2023-10-07 오후 7 56 27" src="https://github.com/jekalmin/extended_openai_conversation/assets/2917984/05e31ea5-daab-4759-b57d-9f5be546bac8">

### 2. script
#### 2-1. Add item to shopping cart
```yaml
- spec:
    name: add_item_to_shopping_cart
    description: Add item to shopping cart
    parameters:
      type: object
      properties:
        item:
          type: string
          description: The item to be added to cart
      required:
      - item
  function:
    type: script
    sequence:
    - service: shopping_list.add_item
      data:
        name: '{{item}}'
```

<img width="300" alt="스크린샷 2023-10-07 오후 7 54 56" src="https://github.com/jekalmin/extended_openai_conversation/assets/2917984/89060728-4703-4e57-8423-354cdc47f0ee">

#### 2-2. Send messages to another messenger

In order to accomplish "send it to Line" like [example3](https://github.com/jekalmin/extended_openai_conversation#3-hook-with-custom-notify-function), register a notify function like below.

```yaml
- spec:
    name: send_message_to_line
    description: Use this function to send message to Line.
    parameters:
      type: object
      properties:
        message:
          type: string
          description: message you want to send
      required:
      - message
  function:
    type: script
    sequence:
    - service: script.notify_all
      data:
        message: "{{ message }}"
```

<img width="300" src="https://github.com/jekalmin/extended_openai_conversation/assets/2917984/16dc4ca0-c823-4dfe-a2b7-1ba7623acc70">

#### 2-3. Get events from calendar

In order to pass result of calling service to OpenAI, set response variable to `_function_result`. 

```yaml
- spec:
    name: get_events
    description: Use this function to get list of calendar events.
    parameters:
      type: object
      properties:
        start_date_time:
          type: string
          description: The start date time in '%Y-%m-%dT%H:%M:%S%z' format
        end_date_time:
          type: string
          description: The end date time in '%Y-%m-%dT%H:%M:%S%z' format
      required:
      - start_date_time
      - end_date_time
  function:
    type: script
    sequence:
    - service: calendar.get_events
      data:
        start_date_time: "{{start_date_time}}"
        end_date_time: "{{end_date_time}}"
      target:
        entity_id:
        - calendar.[YourCalendarHere]
        - calendar.[MoreCalendarsArePossible]
      response_variable: _function_result
```

<img width="300" alt="스크린샷 2023-10-31 오후 9 04 56" src="https://github.com/jekalmin/extended_openai_conversation/assets/2917984/7a6c6925-a53e-4363-a93c-45f63951d41b">

#### 2-4. Play Youtube on TV

```yaml
- spec:
    name: play_youtube
    description: Use this function to play Youtube.
    parameters:
      type: object
      properties:
        video_id:
          type: string
          description: The video id.
      required:
      - video_id
  function:
    type: script
    sequence:
    - service: webostv.command
      data:
        entity_id: media_player.{YOUR_WEBOSTV}
        command: system.launcher/launch
        payload:
          id: youtube.leanback.v4
          contentId: "{{video_id}}"
    - delay:
        hours: 0
        minutes: 0
        seconds: 10
        milliseconds: 0
    - service: webostv.button
      data:
        entity_id: media_player.{YOUR_WEBOSTV}
        button: ENTER
```

<img width="300" src="https://github.com/jekalmin/extended_openai_conversation/assets/2917984/d5c9e0db-8d7c-4a7a-bc46-b043627ffec6">

#### 2-5. Play Netflix on TV

```yaml
- spec:
    name: play_netflix
    description: Use this function to play Netflix.
    parameters:
      type: object
      properties:
        video_id:
          type: string
          description: The video id.
      required:
      - video_id
  function:
    type: script
    sequence:
    - service: webostv.command
      data:
        entity_id: media_player.{YOUR_WEBOSTV}
        command: system.launcher/launch
        payload:
          id: netflix
          contentId: "m=https://www.netflix.com/watch/{{video_id}}"
```

<img width="300" src="https://github.com/jekalmin/extended_openai_conversation/assets/2917984/346065d3-7ab9-49c8-ba30-b79b37a5f084">

### 3. native

#### 3-1. Add automation

Before adding automation, I highly recommend set notification on `automation_registered_via_extended_openai_conversation` event and create separate "Extended OpenAI Assistant" and "Assistant"

(Automation can be added even if conversation fails because of failure to get response message, not automation)

| Create Assistant                                                                                                                             | Notify on created                                                                                                                                                              |
|----------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| <img width="830" alt="1" src="https://github.com/jekalmin/extended_openai_conversation/assets/2917984/b7030a46-9a4e-4ea8-a4ed-03d2eb3af0a9"> | <img width="1116" alt="스크린샷 2023-10-13 오후 6 01 40" src="https://github.com/jekalmin/extended_openai_conversation/assets/2917984/7afa3709-1c1d-41d0-8847-70f2102d824f"> |


Copy and paste below configuration into "Functions"

**For English**
```yaml
- spec:
    name: add_automation
    description: Use this function to add an automation in Home Assistant.
    parameters:
      type: object
      properties:
        automation_config:
          type: string
          description: A configuration for automation in a valid yaml format. Next line character should be \n. Use devices from the list.
      required:
      - automation_config
  function:
    type: native
    name: add_automation
```

**For Korean**
```yaml
- spec:
    name: add_automation
    description: Use this function to add an automation in Home Assistant.
    parameters:
      type: object
      properties:
        automation_config:
          type: string
          description: A configuration for automation in a valid yaml format. Next line character should be \\n, not \n. Use devices from the list.
      required:
      - automation_config
  function:
    type: native
    name: add_automation
```

<img width="300" alt="스크린샷 2023-10-31 오후 9 32 27" src="https://github.com/jekalmin/extended_openai_conversation/assets/2917984/55f5fe7e-b1fd-43c9-bce6-ac92e203598f">

#### 3-2. Get History
Get state history of entities

```yaml
- spec:
    name: get_history
    description: Retrieve historical data of specified entities.
    parameters:
      type: object
      properties:
        entity_ids:
          type: array
          items:
            type: string
            description: The entity id to filter.
        start_time:
          type: string
          description: Start of the history period in "%Y-%m-%dT%H:%M:%S%z".
        end_time:
          type: string
          description: End of the history period in "%Y-%m-%dT%H:%M:%S%z".
      required:
      - entity_ids
  function:
    type: composite
    sequence:
      - type: native
        name: get_history
        response_variable: history_result
      - type: template
        value_template: >-
          {% set ns = namespace(result = [], list = []) %}
          {% for item_list in history_result %}
              {% set ns.list = [] %}
              {% for item in item_list %}
                  {% set last_changed = item.last_changed | as_timestamp | timestamp_local if item.last_changed else None %}
                  {% set new_item = dict(item, last_changed=last_changed) %}
                  {% set ns.list = ns.list + [new_item] %}
              {% endfor %}
              {% set ns.result = ns.result + [ns.list] %}
          {% endfor %}
          {{ ns.result }}
```

<img width="300" src="https://github.com/jekalmin/extended_openai_conversation/assets/2917984/32217f3d-10fc-4001-9028-717b1683573b">

### 4. scrape
#### 4-1. Get current HA version
Scrape version from webpage, "https://www.home-assistant.io"

Unlike [scrape](https://www.home-assistant.io/integrations/scrape/), "value_template" is added at root level in which scraped data from sensors are passed.

```yaml
- spec:
    name: get_ha_version
    description: Use this function to get Home Assistant version
    parameters:
      type: object
      properties:
        dummy:
          type: string
          description: Nothing
  function:
    type: scrape
    resource: https://www.home-assistant.io
    value_template: "version: {{version}}, release_date: {{release_date}}"
    sensor:
      - name: version
        select: ".current-version h1"
        value_template: '{{ value.split(":")[1] }}'
      - name: release_date
        select: ".release-date"
        value_template: '{{ value.lower() }}'
```

<img width="300" alt="스크린샷 2023-10-31 오후 9 46 07" src="https://github.com/jekalmin/extended_openai_conversation/assets/2917984/e640c3f3-8d68-486b-818e-bd81bf71c2f7">

### 5. rest
#### 5-1. Get friend names
- Sample URL: https://jsonplaceholder.typicode.com/users
```yaml
- spec:
    name: get_friend_names
    description: Use this function to get friend_names
    parameters:
      type: object
      properties:
        dummy:
          type: string
          description: Nothing.
  function:
    type: rest
    resource: https://jsonplaceholder.typicode.com/users
    value_template: '{{value_json | map(attribute="name") | list }}'
```

<img width="300" alt="스크린샷 2023-10-31 오후 9 48 36" src="https://github.com/jekalmin/extended_openai_conversation/assets/2917984/f968e328-5163-4c41-a479-76a5406522c1">


### 6. composite
#### 6-1. Search Youtube Music
When using [ytube_music_player](https://github.com/KoljaWindeler/ytube_music_player), after `ytube_music_player.search` service is called, result is stored in attribute of `sensor.ytube_music_player_extra` entity.<br/>


```yaml
- spec:
    name: search_music
    description: Use this function to search music
    parameters:
      type: object
      properties:
        query:
          type: string
          description: The query
      required:
      - query
  function:
    type: composite
    sequence:
    - type: script
      sequence:
      - service: ytube_music_player.search
        data:
          entity_id: media_player.ytube_music_player
          query: "{{ query }}"
    - type: template
      value_template: >-
        media_content_type,media_content_id,title
        {% for media in state_attr('sensor.ytube_music_player_extra', 'search') -%}
          {{media.type}},{{media.id}},{{media.title}}
        {% endfor%}
```

<img width="300" alt="스크린샷 2023-11-02 오후 8 40 36" src="https://github.com/jekalmin/extended_openai_conversation/assets/2917984/648efef8-40d1-45d2-b3f9-9bac4a36c517">

### 7. sqlite
#### 7-1. Let model generate a query
- Without examples, a query tries to fetch data only from "states" table like below
  > Question: When did bedroom light turn on? <br/>
    Query(generated by gpt): SELECT * FROM states WHERE entity_id = 'input_boolean.livingroom_light_2' AND state = 'on' ORDER BY last_changed DESC LIMIT 1
- Since "entity_id" is stored in "states_meta" table, we need to give examples of question and query.
- Not secured, but flexible way

```yaml
- spec:
    name: query_histories_from_db
    description: >-
      Use this function to query histories from Home Assistant SQLite database.
      Example:
        Question: When did bedroom light turn on?
        Answer: SELECT datetime(s.last_updated_ts, 'unixepoch', 'localtime') last_updated_ts FROM states s INNER JOIN states_meta sm ON s.metadata_id = sm.metadata_id INNER JOIN states old ON s.old_state_id = old.state_id WHERE sm.entity_id = 'light.bedroom' AND s.state = 'on' AND s.state != old.state ORDER BY s.last_updated_ts DESC LIMIT 1
        Question: Was livingroom light on at 9 am?
        Answer: SELECT datetime(s.last_updated_ts, 'unixepoch', 'localtime') last_updated, s.state FROM states s INNER JOIN states_meta sm ON s.metadata_id = sm.metadata_id INNER JOIN states old ON s.old_state_id = old.state_id WHERE sm.entity_id = 'switch.livingroom' AND s.state != old.state AND datetime(s.last_updated_ts, 'unixepoch', 'localtime') < '2023-11-17 08:00:00' ORDER BY s.last_updated_ts DESC LIMIT 1
    parameters:
      type: object
      properties:
        query:
          type: string
          description: A fully formed SQL query.
  function:
    type: sqlite
```

Get last changed date time of state | Get state at specific time
--|--
<img width="300" alt="스크린샷 2023-11-19 오후 5 32 56" src="https://github.com/jekalmin/extended_openai_conversation/assets/2917984/5a25db59-f66c-4dfd-9e7b-ae6982ed3cd2"> |<img width="300" alt="스크린샷 2023-11-19 오후 5 32 30" src="https://github.com/jekalmin/extended_openai_conversation/assets/2917984/51faaa26-3294-4f96-b115-c71b268b708e"> 


**FAQ**
1. Can gpt modify or delete data?
    > No, since connection is created in a read only mode, data are only used for fetching. 
2. Can gpt query data that are not exposed in database?
    > Yes, it is hard to validate whether a query is only using exposed entities.
3. Query uses UTC time. Is there any way to adjust timezone?
    > Yes. Set "TZ" environment variable to your [region](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) (eg. `Asia/Seoul`). <br/>
      Or use plus/minus hours to adjust instead of 'localtime' (eg. `datetime(s.last_updated_ts, 'unixepoch', '+9 hours')`).


#### 7-2. Let model generate a query (with minimum validation)
- If need to check at least "entity_id" of exposed entities is present in a query, use "is_exposed_entity_in_query" in combination with "raise".
- Not secured enough, but flexible way
```yaml
- spec:
    name: query_histories_from_db
    description: >-
      Use this function to query histories from Home Assistant SQLite database.
      Example:
        Question: When did bedroom light turn on?
        Answer: SELECT datetime(s.last_updated_ts, 'unixepoch', 'localtime') last_updated_ts FROM states s INNER JOIN states_meta sm ON s.metadata_id = sm.metadata_id INNER JOIN states old ON s.old_state_id = old.state_id WHERE sm.entity_id = 'light.bedroom' AND s.state = 'on' AND s.state != old.state ORDER BY s.last_updated_ts DESC LIMIT 1
        Question: Was livingroom light on at 9 am?
        Answer: SELECT datetime(s.last_updated_ts, 'unixepoch', 'localtime') last_updated, s.state FROM states s INNER JOIN states_meta sm ON s.metadata_id = sm.metadata_id INNER JOIN states old ON s.old_state_id = old.state_id WHERE sm.entity_id = 'switch.livingroom' AND s.state != old.state AND datetime(s.last_updated_ts, 'unixepoch', 'localtime') < '2023-11-17 08:00:00' ORDER BY s.last_updated_ts DESC LIMIT 1
    parameters:
      type: object
      properties:
        query:
          type: string
          description: A fully formed SQL query.
  function:
    type: sqlite
    query: >-
      {%- if is_exposed_entity_in_query(query) -%}
        {{ query }}
      {%- else -%}
        {{ raise("entity_id should be exposed.") }}
      {%- endif -%}
```

#### 7-3. Defined SQL manually
- Use a user defined query, which is verified. And model passes a requested entity to get data from database.
- Secured, but less flexible way
```yaml
- spec:
    name: get_last_updated_time_of_entity
    description: >
      Use this function to get last updated time of entity
    parameters:
      type: object
      properties:
        entity_id:
          type: string
          description: The target entity
  function:
    type: sqlite
    query: >-
      {%- if is_exposed(entity_id) -%}
        SELECT datetime(s.last_updated_ts, 'unixepoch', 'localtime') as last_updated_ts
        FROM states s
          INNER JOIN states_meta sm ON s.metadata_id = sm.metadata_id
          INNER JOIN states old ON s.old_state_id = old.state_id
        WHERE sm.entity_id = '{{entity_id}}' AND s.state != old.state ORDER BY s.last_updated_ts DESC LIMIT 1
      {%- else -%}
        {{ raise("entity_id should be exposed.") }}
      {%- endif -%}
```

## Practical Energy Management Usage

### Real-World Scenarios

**Morning Routine Optimization:**
- "Good morning! What's my overnight energy usage and how can I optimize my morning routine?"
- "Start my water heater 30 minutes before my usual shower time"

**Work Day Energy Savings:**
- "I'm leaving for work, set the house to energy-saving mode"
- "Schedule the dishwasher to run during the cheapest electricity hours today"

**Solar & Battery Management:**
- "How much money did my solar panels save me this month?"
- "When should I charge my electric car to maximize solar usage?"

**Seasonal Optimization:**
- "Prepare my heating system for winter while minimizing energy costs"
- "What's the most efficient temperature setting for my current weather?"

See more energy management [examples](https://github.com/tianzhihe/ha_openai_energy_agent/tree/main/examples).

## Logging & Monitoring
Monitor energy management decisions and API interactions by adding this config to `configuration.yaml`:

```yaml
logger:
  logs:
    custom_components.ha_openai_energy_agent: info
```

## Contributing
This project welcomes contributions focused on energy management features, solar integration, and smart home optimization. Please see our [contribution guidelines](https://github.com/tianzhihe/ha_openai_energy_agent/blob/main/CONTRIBUTING.md).

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support
- 🐛 [Report Issues](https://github.com/tianzhihe/ha_openai_energy_agent/issues)
- 💬 [Discussions](https://github.com/tianzhihe/ha_openai_energy_agent/discussions)
- ⭐ Star this repo if it helps you save energy!
