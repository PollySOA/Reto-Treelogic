import { int, mysqlEnum, mysqlTable, text, timestamp, varchar } from "drizzle-orm/mysql-core";

/**
 * Core user table backing auth flow.
 * Extend this file with additional tables as your product grows.
 * Columns use camelCase to match both database fields and generated types.
 */
export const users = mysqlTable("users", {
  /**
   * Surrogate primary key. Auto-incremented numeric value managed by the database.
   * Use this for relations between tables.
   */
  id: int("id").autoincrement().primaryKey(),
  /** Manus OAuth identifier (openId) returned from the OAuth callback. Unique per user. */
  openId: varchar("openId", { length: 64 }).notNull().unique(),
  name: text("name"),
  email: varchar("email", { length: 320 }),
  loginMethod: varchar("loginMethod", { length: 64 }),
  role: mysqlEnum("role", ["user", "admin"]).default("user").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  lastSignedIn: timestamp("lastSignedIn").defaultNow().notNull(),
});

export type User = typeof users.$inferSelect;
export type InsertUser = typeof users.$inferInsert;

/**
 * Medical studies table for tracking uploaded and processed radiographs
 */
export const medicalStudies = mysqlTable("medical_studies", {
  id: int("id").autoincrement().primaryKey(),
  userId: int("userId").notNull().references(() => users.id),
  fileName: varchar("fileName", { length: 255 }).notNull(),
  fileType: varchar("fileType", { length: 50 }).notNull(), // "png" or "dicom"
  originalImageUrl: text("originalImageUrl"),
  processedImageUrl: text("processedImageUrl"),
  status: mysqlEnum("status", ["pending", "processing", "completed", "failed"]).default("pending").notNull(),
  // Pipeline phase tracking
  phase1Complete: int("phase1Complete").default(0).notNull(),
  phase2Complete: int("phase2Complete").default(0).notNull(),
  phase3Complete: int("phase3Complete").default(0).notNull(),
  phase4Complete: int("phase4Complete").default(0).notNull(),
  // Quality metrics
  psnr: varchar("psnr", { length: 50 }),
  ssim: varchar("ssim", { length: 50 }),
  pseudonymizationHash: varchar("pseudonymizationHash", { length: 255 }),
  // Metadata
  detectedClasses: text("detectedClasses"), // JSON: {name, id, age, date, time}
  boundingBoxes: text("boundingBoxes"), // JSON array of YOLO format boxes
  processingTimeMs: int("processingTimeMs"),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

export type MedicalStudy = typeof medicalStudies.$inferSelect;
export type InsertMedicalStudy = typeof medicalStudies.$inferInsert;

/**
 * Magic Links for secure study access
 */
export const magicLinks = mysqlTable("magic_links", {
  id: int("id").autoincrement().primaryKey(),
  studyId: int("studyId").notNull().references(() => medicalStudies.id),
  token: varchar("token", { length: 255 }).notNull().unique(),
  expiresAt: timestamp("expiresAt").notNull(),
  accessCount: int("accessCount").default(0).notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export type MagicLink = typeof magicLinks.$inferSelect;
export type InsertMagicLink = typeof magicLinks.$inferInsert;