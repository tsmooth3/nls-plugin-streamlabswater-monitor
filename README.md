# StreamLabs Water Monitor Plugin

This plugin integrates with StreamLabs water monitoring system to display water usage statistics on your LED matrix display.

## Features

- Real-time water usage monitoring
- Daily usage breakdown in 8-hour segments (morning, day, evening)
- Historical data visualization
- Monthly and yearly average comparisons
- Maximum usage tracking
- Visual bar graph representation

## Configuration

Create a `config.json` file based on the `config.sample.json` template with the following settings:

```json
{
    "streamlabs_token": "YOUR_STREAMLABS_API_TOKEN",
    "barMax": 112,
    "chartMax": 260,
    "historicalDays": 30
}
```

### Configuration Parameters

- `streamlabs_token`: Your StreamLabs API Bearer token
- `barMax`: Maximum width for the visual bars (default: 112)
- `chartMax`: Maximum value for chart scaling (default: 260)
- `historicalDays`: Number of days to fetch for historical data (default: 30)

## Display Layout

The plugin displays:
- Current daily usage
- Maximum usage
- Monthly average
- Yearly average
- Daily breakdown bars showing usage patterns across morning, day, and evening segments
- Color-coded visualization (morning: light blue, day: dark blue, evening: medium blue)

## Requirements

- StreamLabs Water Monitor system
- Valid StreamLabs API token
- LED Matrix display compatible with the NHL Scoreboard system

## Update Interval

The display updates every 30 seconds with fresh data from the StreamLabs API.

## Installation

1. Copy this plugin to your NHL Scoreboard plugins directory
2. Create a `config.json` file with your StreamLabs API token
3. Enable the plugin in your NHL Scoreboard configuration