document.addEventListener('DOMContentLoaded', () => {
  const queueRoot = document.querySelector('[data-queue-root]');
  if (!queueRoot) {
    return;
  }

  const endpoint = queueRoot.getAttribute('data-endpoint');
  const pollInterval = Number(queueRoot.getAttribute('data-poll-interval') || '15000');
  const avgConsultMinutes = Number(queueRoot.getAttribute('data-avg-consult-minutes') || '0');
  const queuePosition = document.getElementById('queue-position');
  const waitingAhead = document.getElementById('waiting-ahead');
  const tokenStatus = document.getElementById('token-status');
  const queueEta = document.getElementById('queue-eta');

  const updateQueue = async () => {
    try {
      const response = await fetch(endpoint, {
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
        },
      });

      if (!response.ok) {
        return;
      }

      const payload = await response.json();
      if (queuePosition) {
        queuePosition.textContent = String(payload.queue_position);
      }
      if (waitingAhead) {
        waitingAhead.textContent = String(payload.waiting_ahead);
      }
      if (tokenStatus) {
        tokenStatus.textContent = String(payload.status).replace(/^\w/, (character) => character.toUpperCase());
      }
      if (queueEta) {
        queueEta.textContent = String(Number(payload.waiting_ahead || 0) * avgConsultMinutes);
      }
    } catch (error) {
      window.console.debug('Queue polling failed', error);
    }
  };

  updateQueue();
  window.setInterval(updateQueue, pollInterval);
});
