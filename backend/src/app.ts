import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import dotenv from 'dotenv';
import { errorHandler } from './middleware/errorHandler';
import { authRouter } from './routes/auth';
import { plansRouter } from './routes/procurementPlans';
import { lineItemsRouter } from './routes/lineItems';
import { approvalsRouter } from './routes/approvals';
import { purchaseRequisitionsRouter } from './routes/purchaseRequisitions';
import { deliveriesRouter } from './routes/deliveries';
import { stockAssetsRouter } from './routes/stockAssets';
import { exchangeRatesRouter } from './routes/exchangeRates';
import { reportsRouter } from './routes/reports';
import { adminRouter } from './routes/admin';
import { attachmentsRouter } from './routes/attachments';
import { commentsRouter } from './routes/comments';
import { importExportRouter } from './routes/importExport';
import { notificationsRouter } from './routes/notifications';

dotenv.config();

const app = express();

// Security middleware
app.use(helmet());
app.use(cors({
  origin: process.env.CORS_ORIGIN
    ? process.env.CORS_ORIGIN.split(',').map(s => s.trim())
    : ['http://localhost:3000', 'http://localhost:3001', 'http://localhost:3002'],
  credentials: true,
}));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 500,
  standardHeaders: true,
  legacyHeaders: false,
});
app.use('/api/', limiter);

// Body parsing
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// API routes
app.use('/api/v1/auth', authRouter);
app.use('/api/v1/procurement-plans', plansRouter);
app.use('/api/v1/line-items', lineItemsRouter);
app.use('/api/v1/approvals', approvalsRouter);
app.use('/api/v1/purchase-requisitions', purchaseRequisitionsRouter);
app.use('/api/v1/deliveries', deliveriesRouter);
app.use('/api/v1/stock-assets', stockAssetsRouter);
app.use('/api/v1/exchange-rates', exchangeRatesRouter);
app.use('/api/v1/reports', reportsRouter);
app.use('/api/v1/admin', adminRouter);
app.use('/api/v1/attachments', attachmentsRouter);
app.use('/api/v1/comments', commentsRouter);
app.use('/api/v1/import-export', importExportRouter);
app.use('/api/v1/notifications', notificationsRouter);

// Health check
app.get('/api/health', (_req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Error handler
app.use(errorHandler);

export default app;
