/**
 * GraphQL resolvers for the multi-tenant SaaS platform.
 * Handles user queries, mutations, and organization data access.
 */

import { GraphQLError } from "graphql";
import db from "./db";

interface Context {
  user?: { id: string; orgId: string; role: string };
}

// ---------------------------------------------------------------------------
// Query resolvers
// ---------------------------------------------------------------------------

const Query = {
  // VULNERABILITY [OWASP API1 overlap - BOLA]: The user query accepts any
  // user ID and returns the full user object. No ownership or org-scoping
  // check. Subtle: the context.user IS available for checking but isn't used.
  user: async (_: unknown, args: { id: string }, context: Context) => {
    if (!context.user) throw new GraphQLError("Not authenticated");
    // No check: context.user.orgId === targetUser.orgId
    return db.users.findById(args.id);
  },

  // VULNERABILITY [OWASP API4 overlap - Unrestricted Resource Consumption]:
  // The users query allows unbounded first/offset with no max cap.
  // An attacker can dump the entire user table.
  // Subtle: pagination is implemented (looks correct), but there's no upper
  // bound on the 'first' argument.
  users: async (_: unknown, args: { first?: number; offset?: number }, context: Context) => {
    if (!context.user) throw new GraphQLError("Not authenticated");
    const first = args.first ?? 50; // Default 50 but no max
    const offset = args.offset ?? 0;
    const users = await db.users.list({ limit: first, offset });
    return { nodes: users, totalCount: users.length };
  },

  // VULNERABILITY [OWASP API9 overlap - Improper Inventory Management]:
  // Introspection is enabled by default in many GraphQL frameworks.
  // Combined with this resolver exposing internal schema types, an attacker
  // can discover all available queries, mutations, and types.
  __schema: async () => {
    // Explicitly allowing introspection even in production
    return db.getSchema();
  },
};

// ---------------------------------------------------------------------------
// Mutation resolvers
// ---------------------------------------------------------------------------

const Mutation = {
  // VULNERABILITY [OWASP API5 overlap - Broken Function Level Auth]:
  // The deleteUser mutation only checks authentication, not admin role.
  // Subtle: there IS a role check pattern available (context.user.role)
  // but it's not used here.
  deleteUser: async (_: unknown, args: { id: string }, context: Context) => {
    if (!context.user) throw new GraphQLError("Not authenticated");
    // Should check: context.user.role === "admin"
    await db.users.deleteById(args.id);
    return { success: true, deletedId: args.id };
  },

  // VULNERABILITY [OWASP API3 overlap - Broken Object Property Level Auth]:
  // The updateUser mutation accepts an untyped 'input' object, allowing
  // clients to set role, orgId, and other privileged fields.
  // Subtle: GraphQL input types typically enforce a schema, but this
  // resolver spreads the raw input without field-level checks.
  updateUser: async (_: unknown, args: { id: string; input: Record<string, unknown> }, context: Context) => {
    if (!context.user) throw new GraphQLError("Not authenticated");
    const updated = await db.users.updateById(args.id, {
      ...args.input, // Accepts role, orgId, isAdmin — anything
      updatedAt: new Date().toISOString(),
    });
    return updated;
  },

  // VULNERABILITY [OWASP API6 overlap - Unrestricted Business Flow]:
  // Password reset has no rate limiting or account lockout. An attacker
  // can brute-force OTPs or flood a user's email.
  // Subtle: the resolver looks like standard password reset logic.
  requestPasswordReset: async (_: unknown, args: { email: string }) => {
    // No rate limit, no cooldown, no account lockout
    const user = await db.users.findByEmail(args.email);
    if (user) {
      const otp = Math.floor(100000 + Math.random() * 900000).toString();
      await db.otps.create({ userId: user.id, otp, expiresAt: Date.now() + 600_000 });
      // In production: send email with OTP
    }
    // Always return success to prevent user enumeration
    return { success: true, message: "If the email exists, a reset link was sent." };
  },
};

// ---------------------------------------------------------------------------
// Type resolvers
// ---------------------------------------------------------------------------

const User = {
  // VULNERABILITY [OWASP API3 overlap]: Resolves the org field for any user,
  // exposing cross-tenant organization data through nested queries.
  org: async (parent: { orgId: string }) => {
    return db.orgs.findById(parent.orgId);
  },
};

export default { Query, Mutation, User };
