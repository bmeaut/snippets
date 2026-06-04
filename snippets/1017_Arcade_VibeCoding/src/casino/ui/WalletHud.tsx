import React from 'react';

type Props = Readonly<{
  balance?: number;
  onDevTopUp?: () => void;
}>;

export default function WalletHud({ balance = 0, onDevTopUp }: Props) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8, background: 'rgba(0,0,0,0.6)', color: '#fff', padding: '6px 10px', borderRadius: 6 }}>
      <strong>Balance:</strong> {balance} Ft
      {onDevTopUp ? (
        <button
          type="button"
          className="dev-topup-button"
          onClick={onDevTopUp}
          aria-label="Dev Top-up plus 10,000 Ft"
        >
          Dev Top-up (+10,000 Ft)
        </button>
      ) : null}
    </div>
  );
}
