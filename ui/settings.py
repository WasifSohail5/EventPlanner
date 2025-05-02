import streamlit as st
import json
import os
from backend import cache

def show():
    """Settings page"""
    st.title("⚙️ Settings")
    
    # Create tabs for different settings
    theme_tab, cache_tab, about_tab = st.tabs(["Appearance", "Cache", "About"])
    
    with theme_tab:
        st.subheader("🎨 Theme Settings")
        
        # Theme mode
        theme_mode = st.radio(
            "Theme Mode",
            options=["Light", "Dark", "System Default"],
            horizontal=True,
            index=0 if st.session_state.theme == "light" else 
                  1 if st.session_state.theme == "dark" else 2
        )
        
        if theme_mode == "Light":
            st.session_state.theme = "light"
        elif theme_mode == "Dark":
            st.session_state.theme = "dark"
        else:
            st.session_state.theme = "default"
            
        # Primary color
        st.subheader("🎨 Color Theme")
        
        color_options = {
            "Google Blue": "#4285F4",
            "Google Red": "#DB4437",
            "Google Yellow": "#F4B400",
            "Google Green": "#0F9D58",
            "Purple": "#673AB7",
            "Pink": "#E91E63",
            "Teal": "#009688"
        }
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            selected_color_name = st.selectbox(
                "Primary Color",
                options=list(color_options.keys()),
                index=list(color_options.values()).index(st.session_state.primary_color) 
                      if st.session_state.primary_color in list(color_options.values()) else 0
            )
            
        with col2:
            # Show color preview
            selected_color = color_options[selected_color_name]
            st.markdown(
                f"""
                <div style="background-color: {selected_color}; 
                            width: 50px; height: 50px; 
                            border-radius: 5px;"></div>
                """,
                unsafe_allow_html=True
            )
            
        # Update the primary color
        st.session_state.primary_color = color_options[selected_color_name]
        
        # Font settings
        st.subheader("🔤 Text Settings")
        
        font_options = ["System Default", "Sans-serif", "Serif", "Monospace"]
        selected_font = st.selectbox("Font Family", options=font_options)
        
        font_size = st.select_slider(
            "Base Font Size",
            options=["Small", "Medium", "Large"]
        )
        
        # Animation settings
        st.subheader("✨ Effects")
        enable_animations = st.checkbox("Enable Animations", value=True)
        
        # Generate theme preview based on settings
        st.subheader("👁️ Preview")
        
        # Dynamically create preview cards based on selected theme
        background_color = "#ffffff" if st.session_state.theme == "light" else "#121212"
        text_color = "#333333" if st.session_state.theme == "light" else "#f0f0f0"
        card_bg = "#f8f9fa" if st.session_state.theme == "light" else "#1e1e1e"
        
        # Apply preview
        preview_css = f"""
        <style>
        .preview-container {{
            background-color: {background_color};
            color: {text_color};
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        .preview-card {{
            background-color: {card_bg};
            border-left: 4px solid {st.session_state.primary_color};
            padding: 15px;
            border-radius: 4px;
            margin: 10px 0;
        }}
        .preview-button {{
            background-color: {st.session_state.primary_color};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            margin-top: 10px;
        }}
        </style>
        
        <div class="preview-container">
            <h3>Theme Preview</h3>
            <div class="preview-card">
                <strong>Meeting with Team</strong>
                <p>Location: Conference Room</p>
                <button class="preview-button">View Details</button>
            </div>
        </div>
        """
        
        st.markdown(preview_css, unsafe_allow_html=True)
        
        # Save settings
        if st.button("Save Settings", type="primary"):
            st.success("Settings saved successfully!")
            
    with cache_tab:
        st.subheader("🗃️ Cache Management")
        
        # Cache stats
        cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        cache_files = [f for f in os.listdir(cache_dir) if f.endswith('.json')]
        
        if cache_files:
            st.write(f"Cache files: {len(cache_files)}")
            
            # Show cache details
            total_size = 0
            for file in cache_files:
                file_path = os.path.join(cache_dir, file)
                size = os.path.getsize(file_path) / 1024  # KB
                total_size += size
                
                # Read timestamp from cached data
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        timestamp = data.get('timestamp', 0)
                        from datetime import datetime
                        cache_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                        
                except:
                    cache_time = "Unknown"
                
                st.write(f"• {file}: {size:.2f} KB (cached: {cache_time})")
                
            st.write(f"Total cache size: {total_size:.2f} KB")
            
            # Clear cache button
            if st.button("Clear All Cache", type="primary"):
                cache.clear_cache()
                st.success("Cache cleared successfully!")
                st.rerun()
        else:
            st.info("No cache files found")
    
    with about_tab:
        st.subheader("📅 Calendar Manager Pro")
        st.write("Version 1.0")
        st.write("Created by: Wasif Sohail")
        
        st.markdown("""
        #### Features:
        - Create and manage calendar events
        - View upcoming events
        - Smart calendar management
        - Custom themes and settings
        
        #### Credits:
        - Built with Streamlit and Google Calendar API
        """)