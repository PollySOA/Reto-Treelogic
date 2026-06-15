import "dotenv/config";
import express from "express";
import { createServer } from "http";
import net from "net";
import { Readable } from "stream";
import { createExpressMiddleware } from "@trpc/server/adapters/express";
import { registerOAuthRoutes } from "./oauth";
import { registerStorageProxy } from "./storageProxy";
import { appRouter } from "../routers";
import { createContext } from "./context";
import { serveStatic, setupVite } from "./vite";

function isPortAvailable(port: number): Promise<boolean> {
  return new Promise(resolve => {
    const server = net.createServer();
    server.listen(port, () => {
      server.close(() => resolve(true));
    });
    server.on("error", () => resolve(false));
  });
}

async function findAvailablePort(startPort: number = 3000): Promise<number> {
  for (let port = startPort; port < startPort + 20; port++) {
    if (await isPortAvailable(port)) {
      return port;
    }
  }
  throw new Error(`No available port found starting from ${startPort}`);
}

function registerPythonProxy(app: express.Express) {
  const pythonApiUrl = process.env.PYTHON_API_URL || "http://localhost:8000";

  app.use("/api/python", async (req, res) => {
    const upstreamPath = req.originalUrl.replace(/^\/api\/python/, "") || "/";
    const upstreamUrl = new URL(upstreamPath, pythonApiUrl);

    const headers = new Headers();
    for (const [key, value] of Object.entries(req.headers)) {
      if (!value) continue;
      const lowerKey = key.toLowerCase();
      if (["host", "connection", "content-length"].includes(lowerKey)) continue;
      headers.set(key, Array.isArray(value) ? value.join(",") : value);
    }

    try {
      const response = await fetch(upstreamUrl, {
        method: req.method,
        headers,
        body: ["GET", "HEAD"].includes(req.method) ? undefined : req,
        duplex: "half",
      } as RequestInit & { duplex: "half" });

      res.status(response.status);
      response.headers.forEach((value, key) => {
        if (!["connection", "transfer-encoding", "content-encoding"].includes(key.toLowerCase())) {
          res.setHeader(key, value);
        }
      });

      if (!response.body) {
        res.end();
        return;
      }

      Readable.fromWeb(response.body as any).pipe(res);
    } catch (error) {
      console.error("[PythonProxy] failed:", error);
      res.status(502).json({ error: "Python backend unavailable" });
    }
  });
}

async function startServer() {
  const app = express();
  const server = createServer(app);
  registerPythonProxy(app);
  // Configure body parser with larger size limit for file uploads
  app.use(express.json({ limit: "50mb" }));
  app.use(express.urlencoded({ limit: "50mb", extended: true }));
  registerStorageProxy(app);
  registerOAuthRoutes(app);
  // tRPC API
  app.use(
    "/api/trpc",
    createExpressMiddleware({
      router: appRouter,
      createContext,
    })
  );
  // development mode uses Vite, production mode uses static files
  if (process.env.NODE_ENV === "development") {
    await setupVite(app, server);
  } else {
    serveStatic(app);
  }

  const preferredPort = parseInt(process.env.PORT || "3000");
  const port = await findAvailablePort(preferredPort);

  if (port !== preferredPort) {
    console.log(`Port ${preferredPort} is busy, using port ${port} instead`);
  }

  server.listen(port, () => {
    console.log(`Server running on http://localhost:${port}/`);
  });
}

startServer().catch(console.error);
