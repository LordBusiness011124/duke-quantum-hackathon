# Deploying the walkthrough on Vultr

The site is static HTML, CSS, and JavaScript. A small Vultr Cloud Compute
instance is enough. The included container serves it with Nginx.

## Recommended architecture

GitHub is the source of truth. A Vultr Ubuntu instance pulls the private
repository and runs the `site/` container. DNS points a domain or subdomain to
the instance. Caddy or a host-level Nginx proxy can add HTTPS after DNS resolves.

## First deployment

1. Create an Ubuntu LTS Cloud Compute instance in Vultr. The smallest practical
   shared-CPU plan is sufficient for this static site.
2. Add an SSH key during creation. Do not enable password-only root login.
3. Reserve a static IP if the instance's address may change.
4. Add a DNS `A` record, such as `quantum.example.com`, pointing to that IP.
5. In Vultr Firewall, allow TCP 22 from your own IP and TCP 80/443 from anywhere.
6. SSH into the server and install Git and Docker from their official Ubuntu
   installation instructions.
7. Give the server read-only access to the private GitHub repository with a
   GitHub deploy key. Do not copy a personal access token into the repository.
8. Clone the repository, then build and run:

```sh
git clone git@github.com:LordBusiness011124/duke-quantum-hackathon.git
cd duke-quantum-hackathon/site
docker build -t quantum-walkthrough .
docker run -d --name quantum-walkthrough --restart unless-stopped \
  -p 127.0.0.1:8080:80 quantum-walkthrough
```

9. Put Caddy or host Nginx in front of `127.0.0.1:8080` and configure the
   domain. Caddy is a simple option because it obtains and renews TLS
   certificates automatically after DNS is working.

Example Caddy configuration:

```caddyfile
quantum.example.com {
  reverse_proxy 127.0.0.1:8080
  encode zstd gzip
}
```

## Updating the site

After changes are merged to `main`, connect to the instance and run:

```sh
cd duke-quantum-hackathon
git pull --ff-only
cd site
docker build -t quantum-walkthrough .
docker rm -f quantum-walkthrough
docker run -d --name quantum-walkthrough --restart unless-stopped \
  -p 127.0.0.1:8080:80 quantum-walkthrough
```

The next improvement should be a GitHub Actions workflow that connects through
an SSH deploy account and runs this update only after a reviewed change reaches
`main`. Store the SSH key in GitHub Actions secrets, never in the repository.

## Before making the site public

- Replace the G4 snapshot if a later verified submission scores better.
- Resolve or clearly retain the G3 provenance limitation.
- Keep answer CSV files out of the image and public repository. The supplied
  Dockerfile copies only `index.html`, `styles.css`, and `app.js`.
- Confirm the competition permits publishing method details.
- Add a real domain and verify HTTPS.
- Test the page on a phone and with keyboard-only navigation.
