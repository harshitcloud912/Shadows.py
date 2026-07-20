import json
import os
from datetime import datetime
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, DictProperty, ListProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.graphics import Color, Line, Ellipse, Rectangle

# Top-level UI framework dependencies
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRaisedButton

KV = '''
ScreenManager:
    MainScreen:

<MainScreen>:
    name: 'main'
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: 0.04, 0.04, 0.07, 1

        # Global System HUD
        MDBoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(70)
            padding: dp(15)
            spacing: dp(10)
            md_bg_color: 0.07, 0.08, 0.14, 1

            MDBoxLayout:
                orientation: 'vertical'
                MDLabel:
                    text: root.player_title
                    font_style: "Caption"
                    theme_text_color: "Custom"
                    text_color: 0, 0.8, 1, 1
                MDLabel:
                    text: f"{root.player_name} [color=ffb300]Lv.{root.player_level}[/color]"
                    markup: True
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    bold: True

            MDLabel:
                text: f"🔥 STREAK\\n[color=ff6d00]{root.player_streak} Days[/color]"
                markup: True
                halign: "center"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                bold: True

            MDLabel:
                text: f"🪙 GOLD\\n[color=ffd700]{root.player_coins}[/color]"
                markup: True
                halign: "right"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                bold: True

        MDBottomNavigation:
            panel_color: 0.07, 0.08, 0.14, 1
            text_color_active: 0, 0.8, 1, 1

            # --- TAB 1: SYSTEM LOG (QUESTS) ---
            MDBottomNavigationItem:
                name: 'quests_tab'
                text: 'System Log'
                icon: 'sword-cross'
                
                MDBoxLayout:
                    orientation: 'vertical'
                    padding: dp(12)
                    spacing: dp(10)
                    md_bg_color: 0.04, 0.04, 0.07, 1

                    MDBoxLayout:
                        orientation: 'vertical'
                        size_hint_y: None
                        height: dp(50)
                        
                        MDBoxLayout:
                            orientation: 'horizontal'
                            MDLabel:
                                text: "SYSTEM PROG-BAR MATRIX"
                                font_style: "Caption"
                                theme_text_color: "Custom"
                                text_color: 0, 0.8, 1, 1
                            MDLabel:
                                text: f"{root.player_xp} / {root.xp_needed} XP"
                                font_style: "Caption"
                                halign: "right"
                                theme_text_color: "Custom"
                                text_color: 0.6, 0.6, 0.7, 1

                        MDProgressBar:
                            id: xp_bar
                            value: (root.player_xp / root.xp_needed) * 100 if root.xp_needed > 0 else 0
                            color: 0, 0.8, 1, 1
                            size_hint_y: None
                            height: dp(6)

                    ScrollView:
                        MDBoxLayout:
                            id: quest_container
                            orientation: 'vertical'
                            size_hint_y: None
                            height: self.minimum_height
                            spacing: dp(10)

                            MDLabel:
                                text: "ACTIVE COMMAND OBJECTIVES"
                                font_style: "Subtitle2"
                                theme_text_color: "Custom"
                                text_color: 0.4, 0.4, 0.5, 1
                                bold: True

                            MDCard:
                                orientation: 'horizontal'
                                size_hint_y: None
                                height: dp(80)
                                padding: dp(12)
                                md_bg_color: 0.09, 0.1, 0.17, 1
                                radius: [6]
                                
                                MDBoxLayout:
                                    orientation: 'vertical'
                                    MDLabel:
                                        text: "🏃 Daily Trial: Shadow Training"
                                        theme_text_color: "Custom"
                                        text_color: 1, 1, 1, 1
                                        bold: True
                                    MDLabel:
                                        text: "Rewards: +150 XP | +50 Gold"
                                        font_style: "Caption"
                                        theme_text_color: "Custom"
                                        text_color: 0, 0.8, 1, 1
                                
                                MDIconButton:
                                    icon: "check-circle" if root.daily_completed else "circle-outline"
                                    theme_icon_color: "Custom"
                                    icon_color: (0.2, 0.8, 0.4, 1) if root.daily_completed else (0, 0.8, 1, 1)
                                    disabled: root.daily_completed
                                    on_press: app.process_quest_completion("daily_quest", 150, 50, True)

            # --- TAB 2: ACTIVE STATUS ---
            MDBottomNavigationItem:
                name: 'status_tab'
                text: 'Status'
                icon: 'account-circle'
                
                ScrollView:
                    MDBoxLayout:
                        orientation: 'vertical'
                        size_hint_y: None
                        height: self.minimum_height
                        padding: dp(15)
                        spacing: dp(15)
                        md_bg_color: 0.04, 0.04, 0.07, 1

                        MDCard:
                            orientation: 'vertical'
                            size_hint_y: None
                            height: dp(90)
                            padding: dp(12)
                            md_bg_color: 0.09, 0.1, 0.17, 1
                            radius: [8]
                            
                            MDLabel:
                                text: "AVAILABLE STAT CAPITAL"
                                font_style: "Caption"
                                theme_text_color: "Custom"
                                text_color: 0, 0.8, 1, 1
                            MDLabel:
                                text: f"Unassigned Ability Points: {root.stat_points}"
                                font_style: "H6"
                                theme_text_color: "Custom"
                                text_color: 1, 0.7, 0, 1
                                bold: True

                        MDLabel:
                            text: "ATTRIBUTES"
                            font_style: "Subtitle2"
                            theme_text_color: "Custom"
                            text_color: 0.4, 0.4, 0.5, 1
                            bold: True

                        MDCard:
                            orientation: 'vertical'
                            size_hint_y: None
                            height: self.minimum_height
                            padding: dp(10)
                            md_bg_color: 0.07, 0.08, 0.14, 1
                            radius: [6]

                            AttributeEngineRow:
                                title: "STR - Strength"
                                value: str(root.stats_base.get('STR', 10))
                                modifier: f"+{root.stats_mod.get('STR', 0)}"
                                key: "STR"
                            AttributeEngineRow:
                                title: "AGI - Agility"
                                value: str(root.stats_base.get('AGI', 10))
                                modifier: f"+{root.stats_mod.get('AGI', 0)}"
                                key: "AGI"
                            AttributeEngineRow:
                                title: "INT - Intelligence"
                                value: str(root.stats_base.get('INT', 10))
                                modifier: f"+{root.stats_mod.get('INT', 0)}"
                                key: "INT"

            # --- TAB 3: INVENTORY & SHOP ---
            MDBottomNavigationItem:
                name: 'inventory_tab'
                text: 'Store Room'
                icon: 'bag-personal'
                
                ScrollView:
                    MDBoxLayout:
                        orientation: 'vertical'
                        size_hint_y: None
                        height: self.minimum_height
                        padding: dp(15)
                        spacing: dp(15)
                        md_bg_color: 0.04, 0.04, 0.07, 1

                        MDLabel:
                            text: "SYSTEM ARMORY MERCHANDISE"
                            font_style: "Subtitle2"
                            theme_text_color: "Custom"
                            text_color: 0.4, 0.4, 0.5, 1
                            bold: True

                        MDCard:
                            orientation: 'horizontal'
                            size_hint_y: None
                            height: dp(85)
                            padding: dp(12)
                            md_bg_color: 0.09, 0.1, 0.17, 1
                            radius: [6]
                            
                            MDBoxLayout:
                                orientation: 'vertical'
                                MDLabel:
                                    text: "⚔️ Monarch's Dagger"
                                    theme_text_color: "Custom"
                                    text_color: 1, 1, 1, 1
                                    bold: True
                                MDLabel:
                                    text: "Cost: 150 Gold | Attribute: +15 STR"
                                    font_style: "Caption"
                                    theme_text_color: "Custom"
                                    text_color: 1, 0.7, 0, 1
                            
                            MDRaisedButton:
                                text: "ACQUIRE"
                                md_bg_color: 0, 0.5, 0.8, 1
                                on_press: app.execute_shop_purchase("monarch_dagger", 150, "weapon", "STR", 15)

                        MDLabel:
                            text: "EQUIPPED SYSTEM ITEMS"
                            font_style: "Subtitle2"
                            theme_text_color: "Custom"
                            text_color: 0.4, 0.4, 0.5, 1
                            bold: True

                        MDBoxLayout:
                            id: inventory_box
                            orientation: 'vertical'
                            size_hint_y: None
                            height: self.minimum_height
                            spacing: dp(8)

            # --- TAB 4: METRICS LOG ---
            MDBottomNavigationItem:
                name: 'metrics_tab'
                text: 'Analytics'
                icon: 'chart-timeline-variant'
                
                MDBoxLayout:
                    orientation: 'vertical'
                    padding: dp(15)
                    spacing: dp(15)
                    md_bg_color: 0.04, 0.04, 0.07, 1

                    MDLabel:
                        text: "HISTORICAL PERFORMANCE INTERPOLATION"
                        font_style: "Subtitle2"
                        theme_text_color: "Custom"
                        text_color: 0.4, 0.4, 0.5, 1
                        bold: True

                    ActiveLinearGraph:
                        id: engine_graph
                        size_hint_y: None
                        height: dp(200)

# Fixed context references: changed self.* to root.* to point to the rule instance, not the child MDLabels
<AttributeEngineRow@MDBoxLayout>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(45)
    title: ""
    value: "10"
    modifier: "+0"
    key: ""
    
    MDLabel:
        text: root.title
        theme_text_color: "Custom"
        text_color: 0.9, 0.9, 0.9, 1
    MDLabel:
        text: f"{root.value} ({root.modifier})"
        halign: "center"
        theme_text_color: "Custom"
        text_color: 0, 0.8, 1, 1
        bold: True
    MDIconButton:
        icon: "plus-circle-outline"
        theme_icon_color: "Custom"
        icon_color: 0, 0.8, 1, 1
        on_press: app.allocate_stat_node(root.key)
'''

class ActiveLinearGraph(Widget):
    data_stream = ListProperty([0, 0, 0, 0, 0])

    def __init__(self, **kwargs):
        super(ActiveLinearGraph, self).__init__(**kwargs)
        self.bind(pos=self.render_canvas_elements, size=self.render_canvas_elements, data_stream=self.render_canvas_elements)

    def render_canvas_elements(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.07, 0.08, 0.14, 1)
            Rectangle(pos=self.pos, size=self.size)
            
            Color(0.12, 0.13, 0.22, 1)
            for i in range(1, 4):
                y_coord = self.y + (self.height / 4) * i
                Line(points=[self.x, y_coord, self.x + self.width, y_coord], width=1)

        self.canvas.clear()
        if not self.data_stream or len(self.data_stream) < 2:
            return

        with self.canvas:
            Color(0, 0.8, 1, 1)
            vector_coordinates = []
            horizontal_spacing = self.width / (len(self.data_stream) - 1)
            ceiling_value = max(self.data_stream) if max(self.data_stream) > 0 else 10

            for index, value in enumerate(self.data_stream):
                calculated_x = self.x + (index * horizontal_spacing)
                calculated_y = self.y + (value / ceiling_value) * (self.height - dp(30)) + dp(15)
                vector_coordinates.extend([calculated_x, calculated_y])
                
                Ellipse(pos=(calculated_x - dp(4), calculated_y - dp(4)), size=(dp(8), dp(8)))

            Color(0, 0.5, 0.9, 1)
            Line(points=vector_coordinates, width=2)


class MainScreen(Screen):
    player_xp = NumericProperty(0)
    xp_needed = NumericProperty(100)
    player_level = NumericProperty(1)
    player_coins = NumericProperty(0)
    player_streak = NumericProperty(0)
    total_quests_completed = NumericProperty(0)
    stat_points = NumericProperty(0)
    player_name = StringProperty("Jin-Woo")
    player_title = StringProperty("E-RANK RECRUIT")
    daily_completed = BooleanProperty(False)
    
    stats_base = DictProperty({'STR': 10, 'AGI': 10, 'INT': 10})
    stats_mod = DictProperty({'STR': 0, 'AGI': 0, 'INT': 0})
    inventory_data = ListProperty([])
    quest_history = ListProperty([0])

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        Clock.schedule_once(self.load_sandboxed_engine_data, 0)

    def load_sandboxed_engine_data(self, dt):
        app = MDApp.get_running_app()
        self.save_destination = os.path.join(app.user_data_dir, "system_v4_storage.json")
        self.read_state_from_disk()

    def read_state_from_disk(self):
        if os.path.exists(self.save_destination):
            try:
                with open(self.save_destination, "r") as src:
                    payload = json.load(src)
                    self.player_xp = payload.get("xp", 0)
                    self.player_level = payload.get("level", 1)
                    self.player_coins = payload.get("coins", 0)
                    self.player_streak = payload.get("streak", 0)
                    self.total_quests_completed = payload.get("total_quests", 0)
                    self.stat_points = payload.get("stat_points", 0)
                    self.stats_base = payload.get("stats_base", {'STR': 10, 'AGI': 10, 'INT': 10})
                    self.inventory_data = payload.get("inventory", [])
                    self.quest_history = payload.get("quest_history", [0, 0, 0])
                    self.last_quest_timestamp = payload.get("last_quest_timestamp", "")
            except Exception:
                self.apply_base_defaults()
        else:
            self.apply_base_defaults()

        self.recalculate_system_bounds()
        self.reapply_equipment_modifiers()

    def apply_base_defaults(self):
        self.last_quest_timestamp = ""
        self.quest_history = [0, 0, 0]

    def write_state_to_disk(self):
        payload = {
            "xp": self.player_xp,
            "level": self.player_level,
            "coins": self.player_coins,
            "streak": self.player_streak,
            "total_quests": self.total_quests_completed,
            "stat_points": self.stat_points,
            "stats_base": dict(self.stats_base),
            "inventory": list(self.inventory_data),
            "quest_history": list(self.quest_history),
            "last_quest_timestamp": self.last_quest_timestamp
        }
        try:
            with open(self.save_destination, "w") as out:
                json.dump(payload, out)
        except Exception:
            pass

    def recalculate_system_bounds(self):
        self.xp_needed = int(100 * (1.3 ** (self.player_level - 1)))
        
        if self.player_level < 5:
            self.player_title = "E-RANK RECRUIT"
        elif self.player_level < 15:
            self.player_title = "B-RANK STRIKER"
        else:
            self.player_title = "SHADOW MONARCH"

        today_string = datetime.now().strftime("%Y-%m-%d")
        self.daily_completed = (self.last_quest_timestamp == today_string)
        
        if "engine_graph" in self.ids:
            self.ids.engine_graph.data_stream = list(self.quest_history)
            self.ids.engine_graph.render_canvas_elements()

    def reapply_equipment_modifiers(self):
        fresh_modifiers = {'STR': 0, 'AGI': 0, 'INT': 0}
        for element in self.inventory_data:
            if element.get("equipped", False):
                target_stat = element.get("stat_key", "STR")
                fresh_modifiers[target_stat] += element.get("bonus", 0)
        self.stats_mod = fresh_modifiers


class GamifiedApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Cyan"
        return Builder.load_string(KV)

    def on_start(self):
        self.refresh_inventory_interface_tree()

    def process_quest_completion(self, quest_id, xp_reward, coin_reward, affects_streak):
        screen = self.root.get_screen('main')
        current_date = datetime.now().strftime("%Y-%m-%d")

        if quest_id == "daily_quest" and screen.daily_completed:
            return

        if affects_streak and screen.last_quest_timestamp != current_date:
            screen.player_streak += 1
            screen.last_quest_timestamp = current_date
            screen.daily_completed = True

        screen.player_xp += xp_reward
        screen.player_coins += coin_reward
        screen.total_quests_completed += 1

        while screen.player_xp >= screen.xp_needed:
            screen.player_xp -= screen.xp_needed
            screen.player_level += 1
            screen.stat_points += 3
            screen.recalculate_system_bounds()

            anim = Animation(md_bg_color=(0, 0.8, 1, 0.5), duration=0.15) + Animation(md_bg_color=(0.07, 0.08, 0.14, 1), duration=0.3)
            anim.start(screen.ids.xp_bar.parent)

        screen.quest_history.append(screen.total_quests_completed)
        if len(screen.quest_history) > 7:
            screen.quest_history.pop(0)

        screen.recalculate_system_bounds()
        screen.write_state_to_disk()

    def allocate_stat_node(self, target_key):
        screen = self.root.get_screen('main')
        if screen.stat_points > 0:
            screen.stat_points -= 1
            screen.stats_base[target_key] = screen.stats_base.get(target_key, 10) + 1
            screen.write_state_to_disk()

    def execute_shop_purchase(self, item_id, price, slot_type, target_stat, bonus_value):
        screen = self.root.get_screen('main')
        
        for item in screen.inventory_data:
            if item.get("item_id") == item_id:
                return 

        if screen.player_coins >= price:
            screen.player_coins -= price
            
            purchased_payload = {
                "item_id": item_id,
                "label": "Monarch's Dagger",
                "slot": slot_type,
                "stat_key": target_stat,
                "bonus": bonus_value,
                "equipped": False
            }
            screen.inventory_data.append(purchased_payload)
            screen.write_state_to_disk()
            self.refresh_inventory_interface_tree()

    def refresh_inventory_interface_tree(self):
        screen = self.root.get_screen('main')
        
        if "inventory_box" not in screen.ids:
            return
            
        layout_target = screen.ids.inventory_box
        layout_target.clear_widgets()

        for loop_idx, item in enumerate(screen.inventory_data):
            card_item = MDCard(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(70),
                padding=dp(10),
                md_bg_color=(0.07, 0.12, 0.18, 1) if item.get("equipped") else (0.08, 0.09, 0.14, 1),
                radius=[4]
            )
            
            label_text = f"{item.get('label')} ({item.get('stat_key')} +{item.get('bonus')})"
            if item.get("equipped"):
                label_text += " [color=00ff66][ACTIVE][/color]"

            lbl = MDLabel(text=label_text, markup=True, theme_text_color="Custom", text_color=(1,1,1,1))
            card_item.add_widget(lbl)

            action_btn = MDRaisedButton(
                text="UNEQUIP" if item.get("equipped") else "EQUIP",
                md_bg_color=(0.8, 0.2, 0.2, 1) if item.get("equipped") else (0.2, 0.6, 0.4, 1),
                on_press=lambda x, index=loop_idx, c=card_item: self.toggle_equipment_state(index, c)
            )
            card_item.add_widget(action_btn)
            layout_target.add_widget(card_item)

    def toggle_equipment_state(self, index_position, widget_reference):
        screen = self.root.get_screen('main')
        target_item = screen.inventory_data[index_position]
        target_is_equipping = not target_item.get("equipped", False)
        
        if target_is_equipping:
            equip_anim = (
                Animation(elevation=8, md_bg_color=(0, 0.4, 0.6, 1), duration=0.1) + 
                Animation(md_bg_color=(0.07, 0.12, 0.18, 1), duration=0.2)
            )
            equip_anim.start(widget_reference)

        if target_is_equipping and target_item.get("slot") == "weapon":
            for item in screen.inventory_data:
                if item.get("slot") == "weapon":
                    item["equipped"] = False
                    
        target_item["equipped"] = target_is_equipping
        
        screen.inventory_data[index_position] = target_item
        screen.reapply_equipment_modifiers()
        screen.write_state_to_disk()
        self.refresh_inventory_interface_tree()


if __name__ == '__main__':
    GamifiedApp().run()
