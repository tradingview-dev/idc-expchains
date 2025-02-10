#!/usr/bin/env ruby
require 'csv'
require 'optparse'
require 'mechanize'
require "nokogiri"

class TokyoDescriptions

def self.handle_rename_page(results, page)
    Nokogiri::HTML(page.body).xpath("//table[@class='commontbl']/tbody/tr").collect do |row|
        if row.at("td[1]").nil?
            next
        end
        symbol = row.at("td[2]").text.strip
        date = row.at("td[1]").text.strip
        description = ""
        if !row.at("td[3]/a").nil?
            description = row.at("td[3]/a").text
        else
            description = row.at("td[3]").text
        end
        results << {"symbol" => symbol, "date" => date, "description" => description[0, description.length-1].strip}
    end
end

def self.handle_new_page(results, page)
    Nokogiri::HTML(page.body).xpath("//table[@class='commontbl']/tbody/tr").collect do |row|
        if row.at("td[1]").nil?
            next
        end
        symbol = row.at("td[2]").text.strip
        date = row.at("td[1]").text.strip
        description = ""
        if !row.at("td[3]/a").nil?
            description = row.at("td[3]/a").text
        else
            description = row.at("td[3]").text
        end
        results << {"symbol" => symbol, "date" => date, "description" => description[0, description.length-1].strip}
    end
end

def self.handle_consolidate_page(results, page)
    Nokogiri::HTML(page.body).xpath("//table[@class='commontbl']/tbody/tr").collect do |row|
        if row.at("td[1]").nil?
            next
        end
        symbol = row.at("td[2]").text.strip
        date = row.at("td[1]").text.strip
        description = ""
        if !row.at("td[3]/a").nil?
            description = row.at("td[3]/a").text
        else
            description = row.at("td[3]").text
        end
        results << {"symbol" => symbol, "date" => date, "description" => description[0, description.length-1].strip}
    end
end

def self.handle_trade_unit_page(results, page)
    Nokogiri::HTML(page.body).xpath("//table[@class='commontbl']/tbody/tr").collect do |row|
        if row.at("td[1]").nil?
            next
        end
        symbol = row.at("td[2]").text.strip
        date = row.at("td[1]").text.strip
        description = ""
        if !row.at("td[3]/a").nil?
            description = row.at("td[3]/a").text
        else
            description = row.at("td[3]").text
        end
        results << {"symbol" => symbol, "date" => date, "description" => description[0, description.length-1].strip}
    end
end

def self.handle_base_date_page(results, page)
    Nokogiri::HTML(page.body).xpath("//table[@class='commontbl']/tbody/tr").collect do |row|
        if row.at("td[1]").nil?
            next
        end
        symbol = row.at("td[2]").text.strip
        date = row.at("td[1]").text.strip
        description = ""
        if !row.at("td[3]/a").nil?
            description = row.at("td[3]/a").text
        else
            description = row.at("td[3]").text
        end
        results << {"symbol" => symbol, "date" => date, "description" => description[0, description.length-1].strip}
    end
end

def self.handle_split_page(results, page)
    Nokogiri::HTML(page.body).xpath("//table[@class='commontbl']/tbody/tr").collect do |row|
        if row.at("td[1]").nil?
            next
        end
        symbol = row.at("td[2]").text.strip
        date = row.at("td[1]").text.strip
        description = ""
        if !row.at("td[3]/a").nil?
            description = row.at("td[3]/a").text
        else
            description = row.at("td[3]").text
        end
        results << {"symbol" => symbol, "date" => date, "description" => description[0, description.length-1].strip}
    end
end

def self.handle_financial_page(results, page)
    Nokogiri::HTML(page.body).xpath("//table[@class='commontbl']/tbody/tr").collect do |row|
        if row.at("td[1]").nil?
            next
        end
        symbol = row.at("td[1]").text.strip
        date = row.at("td[9]").text.strip
        description = ""
        if !row.at("td[2]/a").nil?
            description = row.at("td[2]/a").text
        else
            description = row.at("td[2]").text
        end
        results << {"symbol" => symbol, "date" => date, "description" => description[0, description.length-1].strip}
    end
end

def self.generate(options)
    agent = Mechanize.new
    results = []
    (1..10).each do |num|
        page = agent.get("http://ca.image.jp/matsui/?type=3&word1=&word2=&sort=1&seldate=0&serviceDatefrom=&serviceDateto=&page=#{num}")
        handle_rename_page(results, page)
    end
    (1..15).each do |num|
        page = agent.get("http://ca.image.jp/matsui/?type=6&word1=&word2=&sort=1&seldate=0&serviceDatefrom=&serviceDateto=&page=#{num}")
        handle_new_page(results, page)
    end
    (1..20).each do |num|
        page = agent.get("http://ca.image.jp/matsui/?type=5&word1=&word2=&sort=1&seldate=0&serviceDatefrom=&serviceDateto=&page=#{num}")
        handle_consolidate_page(results, page)
    end
    (1..25).each do |num|
        page = agent.get("http://ca.image.jp/matsui/?type=7&word1=&word2=&sort=1&seldate=0&serviceDatefrom=&serviceDateto=&page=#{num}")
        handle_trade_unit_page(results, page)
    end
    (1..20).each do |num|
        page = agent.get("http://ca.image.jp/matsui/?type=4&word1=&word2=&sort=1&seldate=0&serviceDatefrom=&serviceDateto=&page=#{num}")
        handle_base_date_page(results, page)
    end
    (1..20).each do |num|
        page = agent.get("http://ca.image.jp/matsui/?word1=&word2=&sort=1&seldate=0&serviceDatefrom=&serviceDateto=&page=#{num}")
        handle_split_page(results, page)
    end
    (1..50).each do |num|
        page = agent.get("http://ca.image.jp/matsui/?type=13&word1=&word2=&sort=1&seldate=0&serviceDatefrom=&serviceDateto=&page=#{num}")
        handle_financial_page(results, page)
    end

    filtered_results = {}
    t_a = Time.new.to_a
    today = "%04d/%02d/%02d" % [t_a[5], t_a[4], t_a[3]]

    results.each do |res|
        if res["date"] > today
            next
        end

        if filtered_results[res["symbol"]].nil?
            filtered_results[res["symbol"]] = res
            next
        end

        if filtered_results[res["symbol"]]["date"] < res["date"]
            filtered_results[res["symbol"]] = res
        end
    end

    csv_string = CSV.generate do |csv|
        filtered_results.each do |symbol, row|
            csv << [ row["symbol"], row["description"] ]
        end
    end
    puts csv_string
end

end

if __FILE__ == $0
    begin
        options = {}
        global = OptionParser.new do |opts|
        end

        TokyoDescriptions.generate(options)
    rescue SystemExit => e
        raise e
    rescue Exception => e
        abort("tokyo_descriptions failed with error: #{e.message}, #{e.backtrace.inspect}")
    end
end
