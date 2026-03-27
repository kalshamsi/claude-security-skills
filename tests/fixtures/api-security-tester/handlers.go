// Package handlers implements Gin-based REST API handlers for the
// multi-tenant SaaS platform's project management service.
package handlers

import (
	"fmt"
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
)

// Project represents a tenant-scoped project resource.
type Project struct {
	ID     int    `json:"id"`
	OrgID  int    `json:"org_id"`
	Name   string `json:"name"`
	Status string `json:"status"`
}

// ProjectUpdate represents allowed update fields.
type ProjectUpdate struct {
	Name   string `json:"name"`
	Status string `json:"status"`
	// VULNERABILITY [OWASP API3 overlap - Broken Object Property Level Auth]:
	// OrgID is in the update struct, meaning a client can transfer a project
	// to a different org by including org_id in the JSON body.
	// Subtle: the struct tag makes it look intentionally serializable.
	OrgID int `json:"org_id,omitempty"`
}

// RegisterRoutes sets up the project management API routes.
func RegisterRoutes(r *gin.Engine) {
	api := r.Group("/api/v1")
	api.Use(AuthMiddleware())

	api.GET("/projects", ListProjects)
	api.GET("/projects/:id", GetProject)
	api.PUT("/projects/:id", UpdateProject)
	api.DELETE("/projects/:id", DeleteProject)

	// VULNERABILITY [OWASP API5 overlap - Broken Function Level Auth]:
	// Admin routes use the same AuthMiddleware as regular routes —
	// no additional admin role check.
	admin := r.Group("/api/v1/admin")
	admin.Use(AuthMiddleware())
	admin.GET("/projects/all", AdminListAllProjects)
	admin.POST("/projects/bulk-delete", AdminBulkDelete)
}

// ---------------------------------------------------------------------------
// Handlers
// ---------------------------------------------------------------------------

// VULNERABILITY [OWASP API1 overlap - BOLA]: GetProject retrieves any
// project by ID without checking if the requesting user's org owns it.
// Subtle: AuthMiddleware IS called, but it only verifies identity, not
// resource ownership.
func GetProject(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid project ID"})
		return
	}
	// Hypothetical DB lookup — no org_id filter
	project := Project{ID: id, OrgID: 1, Name: "Example", Status: "active"}
	c.JSON(http.StatusOK, project)
}

func ListProjects(c *gin.Context) {
	// VULNERABILITY [OWASP API4 overlap - Unrestricted Resource Consumption]:
	// No pagination limit cap. Client can request limit=999999.
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "50"))
	offset, _ := strconv.Atoi(c.DefaultQuery("offset", "0"))
	_ = limit
	_ = offset
	c.JSON(http.StatusOK, gin.H{"projects": []Project{}, "total": 0})
}

func UpdateProject(c *gin.Context) {
	var update ProjectUpdate
	if err := c.ShouldBindJSON(&update); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"updated": true})
}

func DeleteProject(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"deleted": true})
}

func AdminListAllProjects(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"projects": []Project{}})
}

func AdminBulkDelete(c *gin.Context) {
	var body struct {
		IDs []int `json:"ids"`
	}
	if err := c.ShouldBindJSON(&body); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"deleted": len(body.IDs)})
}

// ---------------------------------------------------------------------------
// Middleware
// ---------------------------------------------------------------------------

// AuthMiddleware checks for a valid API key but does NOT enforce RBAC.
func AuthMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		apiKey := c.GetHeader("X-API-Key")
		if apiKey == "" {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "missing API key"})
			return
		}
		// VULNERABILITY [OWASP API2 overlap - Broken Authentication]:
		// Only checks if the API key header is non-empty. No validation
		// against a key store. Subtle: the function name and structure look
		// like real auth middleware.
		c.Set("api_key", apiKey)
		c.Set("user_id", fmt.Sprintf("user-%s", apiKey[:8]))
		c.Next()
	}
}
