import type { ApprovalAction, PurchaseStatus } from '@prs/types';
export class WorkflowError extends Error { constructor(message:string){ super(message); this.name='WorkflowError'; } }
const allowed: Record<PurchaseStatus, Partial<Record<ApprovalAction, PurchaseStatus>>> = {
 DRAFT:{SUBMIT:'PENDING_APPROVAL_L1',UPDATE:'DRAFT',CANCEL:'CANCELLED'},
 PENDING_APPROVAL_L1:{APPROVE:'PENDING_APPROVAL_L2',REJECT:'REJECTED',REQUEST_CLARIFICATION:'CLARIFICATION_REQUIRED',CANCEL:'CANCELLED'},
 PENDING_APPROVAL_L2:{APPROVE:'PENDING_APPROVAL_L3',REJECT:'REJECTED',REQUEST_CLARIFICATION:'CLARIFICATION_REQUIRED',CANCEL:'CANCELLED'},
 PENDING_APPROVAL_L3:{APPROVE:'APPROVED',REJECT:'REJECTED',REQUEST_CLARIFICATION:'CLARIFICATION_REQUIRED',CANCEL:'CANCELLED'},
 CLARIFICATION_REQUIRED:{RESUBMIT:'PENDING_APPROVAL_L1',UPDATE:'CLARIFICATION_REQUIRED',CANCEL:'CANCELLED'},
 APPROVED:{}, REJECTED:{}, CANCELLED:{} };
export function nextStatus(current:PurchaseStatus, action:ApprovalAction, maxLevel=3, previousLevel=1):PurchaseStatus { let next=allowed[current][action]; if(!next) throw new WorkflowError(`Action ${action} is not allowed from ${current}`); if(action==='APPROVE' && current.startsWith('PENDING_APPROVAL_L')){ const level=Number(current.at(-1)); next = level >= maxLevel ? 'APPROVED' : (`PENDING_APPROVAL_L${level+1}` as PurchaseStatus); } if(action==='RESUBMIT') next = `PENDING_APPROVAL_L${previousLevel}` as PurchaseStatus; return next; }
export function levelFromStatus(status:PurchaseStatus):number { const m=status.match(/L(\d)$/); return m ? Number(m[1]) : 0; }
export function totalAmount(items:{total_amount:number}[]):number { return Number(items.reduce((s,i)=>s+i.total_amount,0).toFixed(2)); }
export function calculateLine(qty:number, price:number, tax=0, discount=0):number { const gross=qty*price; return Number((gross - gross*discount/100 + gross*tax/100).toFixed(2)); }
