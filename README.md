# 🌊 Natural Resources Wales River Levels Integration
## 📄 Overview
This Home Assistant integration retrieves river level data from Natural Resources Wales, allowing users to monitor station status, location, and current river levels for selected rivers 🌉.

## 🚨 Requirements
* 🔑 API key (free) from [Natural Resources Wales API Portal](https://api-portal.naturalresources.wales) for "Open Data – River Levels, Rainfall and Sea Data API" 📊
* 🏠 Home Assistant installation

## 🛠️ Configuration
1. 🔓 Obtain an API key from the Natural Resources Wales API Portal.
2. 💻 Add the integration to your Home Assistant configuration, specifying the API key and desired rivers to monitor 🌟.
3. 🕒 Updates are made every 60 seconds by default, adjustable in `const.py` ⏰ - please note that Natural Resources Wales may not update their data this frequently.

## 🎉 Features
* 📊 Retrieve station status, location, and current river levels for selected rivers
* 🔁 Automatic updates every 60 seconds (configurable) 🔄

## 🚀 Getting Started
### HACS Installation
1. Open HACS and click on "Integrations" 📦
2. Click the "+" button in the top right corner to add a new repository 📈
3. Enter `https://github.com/gitStasher/nrw-river-levels` as the repository URL, with type `Integration` as the Type 🌐
4. Click "Add" and then "Install" to install the integration (Natural Resources Wales - River Levels) 💻
5. Restart your Home Assistant when prompted

### Manual Installation
1. Clone the repository using `git clone https://github.com/gitStasher/nrw-river-levels` 📊
2. Copy the `nrw-river-levels` folder into your Home Assistant `custom_components` directory (may not exist if you have no other custom integrations) 📁
3. Restart Home Assistant to load the new integration 🔁

## 💡 Configuration and Usage
1. Configure the integration with your API key and desired rivers.
2. Monitor your river levels in Home Assistant 📈.
