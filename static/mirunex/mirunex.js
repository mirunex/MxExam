(function () {
  'use strict';

  var THEME_KEY = 'mx-theme';
  var menuTriggers = new WeakMap();
  var sidebarPreviousFocus = null;

  function getTargetElement(target) {
    if (target instanceof Element) return target;
    return target && target.parentElement ? target.parentElement : null;
  }

  function updateThemeButtons() {
    var isDark = document.documentElement.dataset.theme !== 'light';

    document.querySelectorAll('[data-mx-theme-toggle]').forEach(function (button) {
      button.setAttribute(
        'aria-label',
        isDark ? 'İşıqlı rejimə keç' : 'Tünd rejimə keç'
      );
      button.setAttribute('aria-pressed', String(!isDark));
    });
  }

  function setTheme(theme) {
    var nextTheme = theme === 'light' ? 'light' : 'dark';
    document.documentElement.dataset.theme = nextTheme;

    try {
      localStorage.setItem(THEME_KEY, nextTheme);
    } catch (_) {
      // Brauzer yaddaşı bağlı ola bilər.
    }

    updateThemeButtons();
  }

  function initializeTheme() {
    try {
      var savedTheme = localStorage.getItem(THEME_KEY);
      if (savedTheme === 'light' || savedTheme === 'dark') {
        document.documentElement.dataset.theme = savedTheme;
      }
    } catch (_) {
      // HTML-də təyin olunmuş tema saxlanılır.
    }

    updateThemeButtons();
  }

  function getDropdownMenu(dropdown) {
    return dropdown ? dropdown.querySelector('.mx-menu') : null;
  }

  function getDropdownTrigger(dropdown) {
    return dropdown
      ? dropdown.querySelector('[data-mx-dropdown-trigger]')
      : null;
  }

  function closeDropdown(dropdown, returnFocus) {
    if (!dropdown) return;

    var menu = getDropdownMenu(dropdown);
    var trigger = getDropdownTrigger(dropdown);

    if (menu) menu.hidden = true;
    if (trigger) trigger.setAttribute('aria-expanded', 'false');

    if (returnFocus && trigger) trigger.focus();
  }

  function closeAllDropdowns(exceptDropdown) {
    document.querySelectorAll('[data-mx-dropdown]').forEach(function (dropdown) {
      if (dropdown !== exceptDropdown) closeDropdown(dropdown, false);
    });
  }

  function openDropdown(dropdown) {
    var menu = getDropdownMenu(dropdown);
    var trigger = getDropdownTrigger(dropdown);

    if (!menu || !trigger) return;

    closeAllDropdowns(dropdown);
    menu.hidden = false;
    trigger.setAttribute('aria-expanded', 'true');

    var firstItem = menu.querySelector(
      '[role="menuitem"]:not([disabled]), .mx-menu__item:not([disabled])'
    );

    if (firstItem) firstItem.focus();
  }

function setSidebarOpen(open) {
  var sidebar = document.getElementById('mx-sidebar');
  var overlay = document.querySelector('[data-mx-overlay]');
  var toggle = document.querySelector('[data-mx-sidebar-toggle]');

  if (!sidebar) return;

  var isDesktop = window.matchMedia('(min-width: 1024px)').matches;

  if (open) {
    sidebarPreviousFocus = document.activeElement;
    sidebar.classList.add('is-open');

    if (overlay) overlay.classList.add('is-open');
    if (toggle) toggle.setAttribute('aria-expanded', 'true');

    sidebar.setAttribute('aria-hidden', 'false');
    sidebar.removeAttribute('inert');

    var firstFocusable = sidebar.querySelector(
      'a[href], button:not([disabled]), input:not([disabled]), [tabindex="0"]'
    );

    if (firstFocusable) firstFocusable.focus();
    else sidebar.focus();

    return;
  }

  sidebar.classList.remove('is-open');

  if (overlay) overlay.classList.remove('is-open');
  if (toggle) toggle.setAttribute('aria-expanded', 'false');

  sidebar.setAttribute('aria-hidden', String(!isDesktop));

  if (isDesktop) sidebar.removeAttribute('inert');
  else sidebar.setAttribute('inert', '');

  if (
    !isDesktop &&
    sidebarPreviousFocus &&
    typeof sidebarPreviousFocus.focus === 'function'
  ) {
    sidebarPreviousFocus.focus();
  }

  sidebarPreviousFocus = null;
}
  function selectTab(tab) {
    var tablist = tab.closest('[role="tablist"]');
    if (!tablist) return;

    var tabs = Array.from(tablist.querySelectorAll('[role="tab"]'));
    var tabContainer = tablist.closest('.mx-tabs') || tablist.parentElement;
    var panels = tabContainer
      ? Array.from(tabContainer.querySelectorAll('[role="tabpanel"]'))
      : [];

    tabs.forEach(function (item, index) {
      var selected = item === tab;
      item.setAttribute('aria-selected', String(selected));
      item.tabIndex = selected ? 0 : -1;

      var panel = null;
      var panelId = item.getAttribute('aria-controls');

      if (panelId) panel = document.getElementById(panelId);
      if (!panel && panels[index]) panel = panels[index];

      if (panel) panel.hidden = !selected;
    });
  }

  function closeToast(toast) {
    if (!toast || toast.classList.contains('is-leaving')) return;

    toast.classList.add('is-leaving');

    window.setTimeout(function () {
      if (toast.parentNode) toast.parentNode.removeChild(toast);
    }, 200);
  }

  function startToastTimers() {
    document.querySelectorAll('.mx-toast').forEach(function (toast) {
      var delay = toast.classList.contains('mx-toast--error') ? 10000 : 6000;

      window.setTimeout(function () {
        closeToast(toast);
      }, delay);
    });
  }

  document.addEventListener('click', function (event) {
    var target = getTargetElement(event.target);
    if (!target) return;

    var themeButton = target.closest('[data-mx-theme-toggle]');
    if (themeButton) {
      setTheme(
        document.documentElement.dataset.theme === 'light' ? 'dark' : 'light'
      );
      return;
    }

    var openButton = target.closest('[data-mx-open]');
    if (openButton) {
      var dialogId = openButton.getAttribute('data-mx-open');
      var dialog = dialogId ? document.getElementById(dialogId) : null;

      if (dialog && typeof dialog.showModal === 'function' && !dialog.open) {
        dialog.showModal();
      }
      return;
    }

    var closeButton = target.closest('[data-mx-close]');
    if (closeButton) {
      var parentDialog = closeButton.closest('dialog');
      if (parentDialog && parentDialog.open) parentDialog.close();
      return;
    }

    var dropdownTrigger = target.closest('[data-mx-dropdown-trigger]');
    if (dropdownTrigger) {
      var dropdown = dropdownTrigger.closest('[data-mx-dropdown]');
      var menu = getDropdownMenu(dropdown);

      if (!dropdown || !menu) return;

      if (menu.hidden) openDropdown(dropdown);
      else closeDropdown(dropdown, false);

      return;
    }

    var menuItem = target.closest(
      '[role="menuitem"], .mx-menu__item'
    );

    if (menuItem) {
      var itemDropdown = menuItem.closest('[data-mx-dropdown]');
      if (itemDropdown) closeDropdown(itemDropdown, false);
      return;
    }

    var tab = target.closest('[role="tab"]');
    if (tab) {
      selectTab(tab);
      return;
    }

    var toastClose = target.closest('[data-mx-toast-close]');
    if (toastClose) {
      closeToast(toastClose.closest('.mx-toast'));
      return;
    }

    var sidebarToggle = target.closest('[data-mx-sidebar-toggle]');
    if (sidebarToggle) {
      var sidebar = document.getElementById('mx-sidebar');
      setSidebarOpen(!(sidebar && sidebar.classList.contains('is-open')));
      return;
    }

    if (target.closest('[data-mx-overlay]')) {
      setSidebarOpen(false);
      return;
    }

    if (target.matches('dialog.mx-dialog')) {
      target.close();
      return;
    }

    document.querySelectorAll('[data-mx-dropdown]').forEach(function (item) {
      if (!item.contains(target)) closeDropdown(item, false);
    });

    if (target.closest('#mx-sidebar') && target.closest('#mx-sidebar a[href]')) {
      setSidebarOpen(false);
    }
  });

  document.addEventListener('keydown', function (event) {
    var target = getTargetElement(event.target);
    if (!target) return;

    var menu = target.closest('.mx-menu');
    if (menu) {
      var dropdown = menu.closest('[data-mx-dropdown]');
      var items = Array.from(
        menu.querySelectorAll(
          '[role="menuitem"]:not([disabled]), .mx-menu__item:not([disabled])'
        )
      );
      var index = items.indexOf(document.activeElement);

      if (event.key === 'Escape') {
        event.preventDefault();
        closeDropdown(dropdown, true);
        return;
      }

      if (event.key === 'Tab') {
        closeDropdown(dropdown, false);
        return;
      }

      var nextIndex = -1;

      if (event.key === 'ArrowDown') nextIndex = (index + 1) % items.length;
      if (event.key === 'ArrowUp') {
        nextIndex = (index - 1 + items.length) % items.length;
      }
      if (event.key === 'Home') nextIndex = 0;
      if (event.key === 'End') nextIndex = items.length - 1;

      if (nextIndex >= 0 && items.length) {
        event.preventDefault();
        items[nextIndex].focus();
        return;
      }
    }

    var tablist = target.closest('[role="tablist"]');
    if (tablist) {
      var tabs = Array.from(tablist.querySelectorAll('[role="tab"]'));
      var currentIndex = tabs.indexOf(target.closest('[role="tab"]'));
      var nextTabIndex = -1;

      if (event.key === 'ArrowRight') {
        nextTabIndex = (currentIndex + 1) % tabs.length;
      }
      if (event.key === 'ArrowLeft') {
        nextTabIndex = (currentIndex - 1 + tabs.length) % tabs.length;
      }
      if (event.key === 'Home') nextTabIndex = 0;
      if (event.key === 'End') nextTabIndex = tabs.length - 1;

      if (nextTabIndex >= 0 && tabs.length) {
        event.preventDefault();
        tabs[nextTabIndex].focus();
        selectTab(tabs[nextTabIndex]);
        return;
      }
    }

    if (event.key === 'Escape') {
      var openSidebar = document.getElementById('mx-sidebar');
      if (openSidebar && openSidebar.classList.contains('is-open')) {
        setSidebarOpen(false);
      }
    }
  });

  document.addEventListener('change', function (event) {
    var target = getTargetElement(event.target);
    if (!target || !target.matches('.mx-dropzone input[type="file"]')) return;

    var dropzone = target.closest('.mx-dropzone');
    var fileName = dropzone
      ? dropzone.querySelector('[data-mx-file-name]')
      : null;

    if (!fileName) return;

    fileName.textContent =
      target.files && target.files.length
        ? Array.from(target.files).map(function (file) {
            return file.name;
          }).join(', ')
        : '';
  });

  document.addEventListener('click', function (event) {
    var target = getTargetElement(event.target);
    if (!target) return;

    document.querySelectorAll('[data-mx-dropdown]').forEach(function (dropdown) {
      if (!dropdown.contains(target)) closeDropdown(dropdown, false);
    });
  }, true);

  window.addEventListener('DOMContentLoaded', function () {
    initializeTheme();
    startToastTimers();

    var sidebar = document.getElementById('mx-sidebar');
    if (sidebar && !sidebar.classList.contains('is-open')) {
      sidebar.setAttribute('aria-hidden', 'true');
      sidebar.setAttribute('inert', '');
    }

    document.querySelectorAll('[data-mx-dropdown]').forEach(function (dropdown) {
      var trigger = getDropdownTrigger(dropdown);
      var menu = getDropdownMenu(dropdown);

      if (trigger) {
        trigger.setAttribute('aria-haspopup', 'menu');
        trigger.setAttribute('aria-expanded', 'false');
      }

      if (menu) menu.hidden = true;
    });

    document.querySelectorAll('[role="tablist"]').forEach(function (tablist) {
      var selected =
        tablist.querySelector('[role="tab"][aria-selected="true"]') ||
        tablist.querySelector('[role="tab"]');

      if (selected) selectTab(selected);
    });
  });

  var desktopQuery = window.matchMedia('(min-width: 1024px)');

  function closeSidebarOnDesktop(event) {
    if (event.matches) setSidebarOpen(false);
  }

  if (desktopQuery.addEventListener) {
    desktopQuery.addEventListener('change', closeSidebarOnDesktop);
  } else if (desktopQuery.addListener) {
    desktopQuery.addListener(closeSidebarOnDesktop);
  }

  initializeTheme();
})();