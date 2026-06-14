<div align="center">
  <h2 align="center">The Healthy Lab</h2>

  The Healthy Lab is a fully responsive healthy food website, <br />built using HTML, CSS, and JavaScript.

  <a href="https://ducanhthecodingbeast.github.io/The-Heallthy-Lab/"><strong>➥ Live Demo</strong></a>

</div>

<br />

### Run Locally

To run **The Healthy Lab** locally, run this command in your terminal:

```bash
git clone https://github.com/ducanhthecodingbeast/The-Heallthy-Lab.git
```

### Live Demo (GitHub Pages)

To view the live demo online, this project uses GitHub Pages. 
If the link above doesn't work yet, make sure GitHub Pages is enabled in your repository settings!

### Run With Docker

From the project folder, run:

```bash
docker compose up --build
```

Then open:

```text
http://localhost:5500
```

You can also build and run without Compose:

```bash
docker build -t the-healthy-lab .
docker run --rm -p 5500:5500 the-healthy-lab
```

### VS Code Live Server

The Live Server port is set to `5500` in `.vscode/settings.json`, so **Go Live** also opens the site at:

```text
http://localhost:5500
```
