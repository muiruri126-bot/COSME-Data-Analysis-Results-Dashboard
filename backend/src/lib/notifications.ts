import nodemailer from 'nodemailer';
import prisma from './prisma';

// ---------------------------------------------------------------------------
// Email transporter — uses SMTP if configured, otherwise logs to console
// ---------------------------------------------------------------------------
const smtpHost = process.env.SMTP_HOST;
const smtpPort = parseInt(process.env.SMTP_PORT || '587', 10);
const smtpUser = process.env.SMTP_USER;
const smtpPass = process.env.SMTP_PASS;
const smtpFrom = process.env.SMTP_FROM || 'COSME Procurement <noreply@cosme.org>';

const transporter = smtpHost
  ? nodemailer.createTransport({
      host: smtpHost,
      port: smtpPort,
      secure: smtpPort === 465,
      auth: smtpUser ? { user: smtpUser, pass: smtpPass } : undefined,
    })
  : null;

async function sendEmail(to: string, subject: string, html: string) {
  if (transporter) {
    try {
      await transporter.sendMail({ from: smtpFrom, to, subject, html });
    } catch (err) {
      console.error('Email send failed:', err);
    }
  } else if (process.env.NODE_ENV === 'development') {
    console.log(`[EMAIL] To: ${to} | Subject: ${subject}`);
  }
}

// ---------------------------------------------------------------------------
// Notification types
// ---------------------------------------------------------------------------
export type NotificationType =
  | 'SUBMITTED'
  | 'APPROVED'
  | 'RETURNED'
  | 'CANCELLED'
  | 'PR_RAISED'
  | 'DELIVERED';

// ---------------------------------------------------------------------------
// Core: create in-app notification + send email
// ---------------------------------------------------------------------------
interface NotifyParams {
  userId: string;
  type: NotificationType;
  title: string;
  message: string;
  lineItemId?: string;
  headerId?: string;
}

export async function createNotification(params: NotifyParams) {
  // In-app notification
  const notif = await prisma.notification.create({
    data: {
      userId: params.userId,
      type: params.type,
      title: params.title,
      message: params.message,
      lineItemId: params.lineItemId,
      headerId: params.headerId,
    },
  });

  // Send email asynchronously (don't block workflow)
  const user = await prisma.user.findUnique({
    where: { id: params.userId },
    select: { email: true, fullName: true },
  });
  if (user) {
    const html = `
      <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;">
        <div style="background:#003b7c;color:#fff;padding:16px 24px;border-radius:8px 8px 0 0;">
          <h2 style="margin:0;font-size:18px;">COSME Procurement Tracker</h2>
        </div>
        <div style="padding:24px;border:1px solid #e0e0e0;border-top:none;border-radius:0 0 8px 8px;">
          <p>Hi ${user.fullName},</p>
          <h3 style="color:#003b7c;">${params.title}</h3>
          <p>${params.message}</p>
          <hr style="border:none;border-top:1px solid #eee;margin:20px 0;" />
          <p style="color:#888;font-size:12px;">
            This is an automated notification from the COSME Procurement Tracker.
          </p>
        </div>
      </div>
    `;
    sendEmail(user.email, `[COSME] ${params.title}`, html).catch(() => {});
  }

  return notif;
}

// ---------------------------------------------------------------------------
// Workflow notification helpers
// ---------------------------------------------------------------------------

/**
 * When a requester submits a line item → notify the department manager
 */
export async function notifySubmitted(opts: {
  lineItemId: string;
  lineItemRef: string;
  headerId: string;
  submittedBy: string; // user full name
  departmentManagerId: string;
}) {
  return createNotification({
    userId: opts.departmentManagerId,
    type: 'SUBMITTED',
    title: 'New Item Submitted for Approval',
    message: `<strong>${opts.submittedBy}</strong> submitted line item <strong>${opts.lineItemRef}</strong> for your approval.`,
    lineItemId: opts.lineItemId,
    headerId: opts.headerId,
  });
}

/**
 * When manager approves → notify the requester (plan creator)
 */
export async function notifyApproved(opts: {
  lineItemId: string;
  lineItemRef: string;
  headerId: string;
  approvedBy: string;
  createdById: string;
  comment?: string;
}) {
  const commentLine = opts.comment ? `<br/>Comment: <em>"${opts.comment}"</em>` : '';
  return createNotification({
    userId: opts.createdById,
    type: 'APPROVED',
    title: 'Line Item Approved',
    message: `Your line item <strong>${opts.lineItemRef}</strong> has been approved by <strong>${opts.approvedBy}</strong>.${commentLine}`,
    lineItemId: opts.lineItemId,
    headerId: opts.headerId,
  });
}

/**
 * When manager returns → notify the requester
 */
export async function notifyReturned(opts: {
  lineItemId: string;
  lineItemRef: string;
  headerId: string;
  returnedBy: string;
  createdById: string;
  comment?: string;
}) {
  const commentLine = opts.comment ? `<br/>Comment: <em>"${opts.comment}"</em>` : '';
  return createNotification({
    userId: opts.createdById,
    type: 'RETURNED',
    title: 'Line Item Returned for Correction',
    message: `Your line item <strong>${opts.lineItemRef}</strong> has been returned by <strong>${opts.returnedBy}</strong>. Please review and resubmit.${commentLine}`,
    lineItemId: opts.lineItemId,
    headerId: opts.headerId,
  });
}

/**
 * When item is cancelled → notify the requester
 */
export async function notifyCancelled(opts: {
  lineItemId: string;
  lineItemRef: string;
  headerId: string;
  cancelledBy: string;
  createdById: string;
  reason?: string;
}) {
  const reasonLine = opts.reason ? `<br/>Reason: <em>"${opts.reason}"</em>` : '';
  return createNotification({
    userId: opts.createdById,
    type: 'CANCELLED',
    title: 'Line Item Cancelled',
    message: `Line item <strong>${opts.lineItemRef}</strong> has been cancelled by <strong>${opts.cancelledBy}</strong>.${reasonLine}`,
    lineItemId: opts.lineItemId,
    headerId: opts.headerId,
  });
}

/**
 * When PR is raised → notify the requester
 */
export async function notifyPRRaised(opts: {
  lineItemId: string;
  lineItemRef: string;
  headerId: string;
  createdById: string;
  prNumber: string;
}) {
  return createNotification({
    userId: opts.createdById,
    type: 'PR_RAISED',
    title: 'Purchase Requisition Raised',
    message: `A purchase requisition (<strong>${opts.prNumber}</strong>) has been raised for your line item <strong>${opts.lineItemRef}</strong>.`,
    lineItemId: opts.lineItemId,
    headerId: opts.headerId,
  });
}

/**
 * When delivery is recorded → notify the requester
 */
export async function notifyDelivered(opts: {
  lineItemId: string;
  lineItemRef: string;
  headerId: string;
  createdById: string;
  quantity: number;
}) {
  return createNotification({
    userId: opts.createdById,
    type: 'DELIVERED',
    title: 'Delivery Recorded',
    message: `A delivery of <strong>${opts.quantity}</strong> unit(s) has been recorded for line item <strong>${opts.lineItemRef}</strong>.`,
    lineItemId: opts.lineItemId,
    headerId: opts.headerId,
  });
}
