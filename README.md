Introduction -3 min- 
Platform Engineering -4 min-, and a reminder to view the previous DevOps talk  
Platform Engineering Questions
Where is the platform?

How can we host it?

How can we use it?

We need to develop it. But we are DevOps, we need efficiency to bring efficiency. 

Platform Engineering Programming Framework
The framework is used to develop tools that integrates with 3rd party applications e.g. Github, Confluence, Teams, TeamCity, Bitbucket.

Data source: (3rd party applications, e.g. Jira, GitHub, Teams, TeamCity ..etc)

Software architecture (Model-View-Controller/MVC architecture)

Programming language (Python)

Output: Python/pip packages hosed on PyPI repository

PyPI hosted on Nexus

Build packages: all scripted

Deployment and publishing is scripted

Optional CI, since all the CI steps can be done locally and more efficiently

Anything expected to be done frequently is automated into one make -Makefile- command

Benefits of an Efficient Programming Framework
Advantages stuff

Demo The Framework
Connectors are used for API integration and data management

Models are the logic blocks, representing the targeted tool logic

Controllers are the interfaces with the end-user 

Next Steps For The Framework
More functionalities in the connectors

Integrate with more 3rd party applications, e.g. Jira, GitHub Actions

Integration with data visualization tools (Grafana, PowerPI)

Publishing the framework to an open source framework

Q&A
20 to 30 minutes

Remember to use visuals, diagrams, and examples in the document.