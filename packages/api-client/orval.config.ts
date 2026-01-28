import { defineConfig } from "orval";

export default defineConfig({
    queroplantao: {
        input: {
            target: "./openapi.json",
        },
        output: {
            mode: "tags-split",
            target: "./src/client/generated",
            schemas: "./src/client/models",
            client: "react-query",
            httpClient: "fetch",
            clean: true,
            prettier: true,
            override: {
                mutator: {
                    path: "./src/client/custom-fetch.ts",
                    name: "customFetch",
                },
                useTypeOverInterfaces: true,
                useDates: true,
                query: {
                    useQuery: true,
                    useMutation: true,
                    useInfinite: false, // Disable infinite queries for now (type issues)
                    useErrorBoundary: true, // Enable error type generation
                    options: {
                        staleTime: 30000,
                    },
                },
            },
        },
    },
});
