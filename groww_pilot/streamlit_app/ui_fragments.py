def get_scrollbar_css():
    return '''
    <style>
    .scroll-list-container {
        max-height: 600px;
        overflow-y: auto;
        padding-right: 8px;
    }
    .scroll-list-container::-webkit-scrollbar {
        width: 8px;
        background: #f1f1f1;
        border-radius: 8px;
    }
    .scroll-list-container::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 8px;
    }
    .scroll-list-container::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
    </style>
    '''

def get_scrollable_radio_start():
    return '<div class="scroll-list-container">'

def get_scrollable_radio_end():
    return '</div>'
