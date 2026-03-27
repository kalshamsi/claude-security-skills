package com.saas.platform.api;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

import java.util.*;

/**
 * Spring Boot REST controller for the multi-tenant SaaS platform.
 * Handles tenant configuration and reporting endpoints.
 */
@RestController
@RequestMapping("/api/v1")
public class ApiController {

    @Value("${app.internal.base-url:http://localhost:8081}")
    private String internalBaseUrl;

    private final RestTemplate restTemplate = new RestTemplate();

    // -----------------------------------------------------------------------
    // Tenant configuration
    // -----------------------------------------------------------------------

    /**
     * VULNERABILITY [OWASP API3 overlap - Broken Object Property Level Auth]:
     * Accepts any map of fields for tenant update, including billing_tier,
     * max_users, and feature_flags which should be platform-admin-only.
     * Subtle: using Map<String, Object> looks like a flexible API design
     * pattern. The "admin fields" aren't visibly distinguished.
     */
    @PutMapping("/tenants/{tenantId}/config")
    public ResponseEntity<Map<String, Object>> updateTenantConfig(
            @PathVariable String tenantId,
            @RequestBody Map<String, Object> config) {
        // No field-level authorization — accepts billing_tier, max_users, etc.
        config.put("tenant_id", tenantId);
        config.put("updated_at", new Date());
        return ResponseEntity.ok(config);
    }

    // -----------------------------------------------------------------------
    // Reporting — SSRF via report export
    // -----------------------------------------------------------------------

    /**
     * VULNERABILITY [OWASP API7 overlap - SSRF]: The callback_url parameter
     * is used to POST the generated report. No URL validation or allowlist.
     * Subtle: "callback URL for report delivery" is a legitimate webhook
     * pattern. The SSRF risk isn't obvious.
     */
    @PostMapping("/reports/export")
    public ResponseEntity<Map<String, String>> exportReport(
            @RequestBody Map<String, Object> request) {
        String callbackUrl = (String) request.get("callback_url");
        String reportId = UUID.randomUUID().toString();

        // In a real app, this would be async. Here we simulate the callback.
        if (callbackUrl != null) {
            restTemplate.postForEntity(callbackUrl,
                    Map.of("report_id", reportId, "status", "complete"),
                    String.class);
        }

        return ResponseEntity.ok(Map.of("report_id", reportId, "status", "queued"));
    }

    // -----------------------------------------------------------------------
    // Internal/debug endpoints
    // -----------------------------------------------------------------------

    /**
     * VULNERABILITY [OWASP API8 overlap - Security Misconfiguration]:
     * Exposes environment variables and system properties via an unauthenticated
     * endpoint. Subtle: under /internal/ path, assumed to be network-gated.
     */
    @GetMapping("/internal/env")
    public ResponseEntity<Map<String, Object>> getEnvironment() {
        Map<String, Object> env = new HashMap<>();
        env.put("java_version", System.getProperty("java.version"));
        env.put("os", System.getProperty("os.name"));
        env.put("database_url", System.getenv("DATABASE_URL"));
        env.put("api_keys_configured", System.getenv("API_KEYS") != null);
        return ResponseEntity.ok(env);
    }

    // -----------------------------------------------------------------------
    // API versioning / inventory
    // -----------------------------------------------------------------------

    /**
     * VULNERABILITY [OWASP API9 - Improper Inventory Management]:
     * Multiple API versions coexist. The v0 endpoint lacks authentication
     * and was supposed to be deprecated but is still routable.
     * Subtle: it's defined as a separate method with a different path,
     * easy to miss during code review.
     */
    @GetMapping("/v0/tenants/{tenantId}")
    public ResponseEntity<Map<String, Object>> getTenantLegacy(
            @PathVariable String tenantId) {
        // No authentication — this was the pre-auth MVP endpoint
        return ResponseEntity.ok(Map.of(
                "tenant_id", tenantId,
                "name", "Legacy Tenant",
                "api_version", "v0",
                "deprecated", true
        ));
    }
}
