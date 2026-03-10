# Working memory experiment

Smile-based online experiment of the probed serial recall working memory task with additional AI checks.

## Setup

For instructions on how to properly setup smile, please see [smile.gureckislab.org](https://smile.gureckislab.org).
Here we provide instructions to run the experiment offline for illustrative purposes (no data will be collected).

First install all node dependencies (this assumes `npm` is installed on your system).

```bash
npm run setup_project
```

Then locally start the experiment and navigate to [http://localhost:3020/head/](http://localhost:3020/head/).

## Running an LLM participant

There are many browser automation tools available that can be used to see how an LLM performs on this experiment.
One way is to use the [agent-browser](https://agent-browser.dev/) tool which is part of the Node.js dependencies of this repo already.
To watch it perform the experiment in Chrome, start the experiment in a connected Chrome instance like so

```bash
# Terminal window 1
npm run dev:live
# Terminal window 2
chrome --remote-debugging-port=9222
# Terminal window 3
npx agent-browser connect 9222
npx agent-browser open http://localhost:3020/head/
```

Then you can run your agent of choice in Terminal window 3 with the following example instructions:

```text
We are inside a repository that has a tool called agent-browser installed that allows you to control a website. You can run it using `npx agent-browser --help` . Please use this tool to perform my experiment at http://localhost:3020/head/. I want you to do the whole experiment to make sure it works as intended.

I have already run the following commands

chrome --remote-debugging-port=9222 &
npx agent-browser connect 9222
npx agent-browser open http://localhost:3020/head/

So you are ready to start.
First run `npx agent-browser --help` to see how to use agent-browser.
Then run `npx agent-browser snapshot` to get started with the experiment.
```
