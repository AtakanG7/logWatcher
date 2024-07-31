LogWatcher: Simplifying Docker Image Monitoring

https://github.com/user-attachments/assets/5302ce2d-b788-4d97-8a7d-f8b1693bc6e9

LogWatcher is an open-source software tool created by Atakan G. to simplify application monitoring for Docker images. This project provides an easy-to-use interface for developers to gain insights about their Docker applications, monitor resource usage, and optimize performance.
Features

    Real-time monitoring of Docker images
    Resource usage tracking and optimization
    Error log monitoring in real-time



    Alerting system for critical events
    Benchmarking capabilities
    Configuration management through a user-friendly interface
    Container management from the dashboard

Getting Started

    Clone the repository: git clone https://github.com/AtakanG7/logWatcher.git
    Run the starter script: sh logwatcher.sh your-docker-image-name
    Wait for the requirements to be installed. A Streamlit interface will launch automatically.

Architecture

LogWatcher utilizes a microservices architecture, with each service operating independently and communicating through Docker network interfaces over HTTP/HTTPS protocols. The system includes:

    Prometheus: Metric scraper for collecting information from registered network devices
    Grafana: Provides graphical interfaces using Prometheus data
    Alert Manager: Listens for alerts from Prometheus and takes appropriate actions
    Loki & Promtail: Collects log information from target container applications
    Node Exporter & Cadvisor: Gathers information about the local system and Docker containers

Benefits

    Quick and easy testing of ready Docker images
    Comprehensive resource usage monitoring
    Real-time error log visibility
    Simplified configuration management
    Automated setup of monitoring tools
    Scalable architecture for future expansion

Use Cases

    Rapid testing and evaluation of Docker images
    Resource usage optimization
    Continuous monitoring for error detection
    Internal company monitoring solution

Technology Stack

    Streamlit: User interface creation
    Prometheus: Metric collection and querying
    Grafana: Data visualization
    Alert Manager: Alert handling and notification
    Loki & Promtail: Log aggregation and processing
    Node Exporter & Cadvisor: System and container metrics collection
    Docker: Containerization and networking

Future Plans

    Integration with cloud platforms
    Improved compatibility with various tools

Contributing

This project is open-source and welcomes community contributions. Feel free to submit issues, feature requests, or pull requests to help improve LogWatcher.
Resources

For more information on the technologies and concepts used in LogWatcher, refer to the following resources:

    Microservices architecture
    Docker documentation
    Prometheus documentation
    Grafana dashboards
    Streamlit documentation

License

[Include license information here]
Contact

For questions or support, please contact Atakan G. [Include contact information if available]

Note: As of July 31, 2024, the AtakanG7 GitHub repository may not be publicly accessible. Please check for updates or alternative sources for the project.
