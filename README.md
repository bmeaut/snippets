# snippets
A set of example-based tutorials for various classes

## Run locally 

To test the webpage locally, you can serve the page using docker. On Windows, you can preferably use Docker Desktop.

1. Open a terminal in the root of the repository.

1. Run the following command in case of Windows (PowerShell), Linux or MacOS:

```bash
docker run --rm  -v ${PWD}:/srv/jekyll -p 4000:4000 jekyll/jekyll jekyll serve
```

1. Open the [http://localhost:4000/snippets/](http://localhost:4000/snippets/) link in a browser.
